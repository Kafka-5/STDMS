from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def mark_absent_students(self, token_id):
    # Defer model imports to inside the task
    from teacher.models import AttendanceToken
    from student.models import StudentProfile, Attendance, Subject
    
    logger.info(f"Starting mark_absent_students for token ID {token_id}, attempt {self.request.retries + 1}")
    try:
        token = AttendanceToken.objects.get(id=token_id)
        logger.info(f"Found token {token.token}, created at {token.created_at}, processed: {token.processed}")
        if token.processed:
            logger.info(f"Token {token.token} already processed. Skipping.")
            return
        expiration_time = token.created_at + timezone.timedelta(minutes=7, seconds=30)
        current_time = timezone.now()
        logger.info(f"Current time: {current_time}, Expiration time: {expiration_time}")
        if current_time <= expiration_time:
            time_remaining = (expiration_time - current_time).total_seconds()
            logger.info(f"Token {token.token} not yet expired. Retrying in {time_remaining:.2f} seconds.")
            raise self.retry(countdown=max(1, int(time_remaining)))
        subject = token.subject
        today = timezone.now().date()
        logger.info(f"Processing absent marking for subject {subject.name} on {today}")
        students = StudentProfile.objects.filter(subjects=subject)
        logger.info(f"Found {students.count()} students enrolled in subject {subject.name}")
        if not students.exists():
            logger.info(f"No students enrolled in subject {subject.name}. Marking token as processed.")
            token.processed = True
            token.save()
            return
        present_students = token.used_by.all()
        logger.info(f"Found {present_students.count()} students who marked attendance")
        for student in students:
            if student in present_students:
                logger.info(f"Student {student.user.username} already marked present. Skipping.")
                continue
            attendance = Attendance.objects.filter(
                student=student,
                subject=subject,
                date=today
            ).first()
            if attendance:
                if not attendance.present:
                    logger.info(f"Student {student.user.username} already marked absent. Skipping.")
                    continue
                else:
                    logger.info(f"Student {student.user.username} has present record. Updating to absent.")
                    attendance.present = False
                    attendance.save()
                    logger.info(f"Updated {student.user.username} to absent for {subject.name} on {today}.")
            else:
                logger.info(f"Creating absent record for student {student.user.username}")
                try:
                    Attendance.objects.create(
                        student=student,
                        subject=subject,
                        date=today,
                        present=False
                    )
                    logger.info(f"Marked {student.user.username} as absent for {subject.name} on {today}.")
                except Exception as e:
                    logger.error(f"Failed to create absent record for {student.user.username}: {str(e)}", exc_info=True)
        token.processed = True
        token.save()
        logger.info(f"Completed absent marking for token {token.token}.")
    except AttendanceToken.DoesNotExist:
        logger.error(f"Token with ID {token_id} not found.")
    except Exception as e:
        logger.error(f"Error in mark_absent_students for token {token_id}: {str(e)}", exc_info=True)
        raise