"""
Celery 应用配置
初始化 Celery 应用并设置相关配置
"""

from celery import Celery
from app.core.config import settings

# 创建 Celery 实例
celery_app = Celery(
    'edu_feedback_analysis',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.analysis.machine_learing.tasks.celery_tasks']
)

# Celery 配置
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    task_soft_time_limit=3300,  # 55分钟软超时
    worker_prefetch_multiplier=1,  # 确保一个worker一次只处理一个任务
    worker_max_tasks_per_child=1,  # 每个worker进程处理完一个任务后重启，防止内存泄漏
    result_expires=3600,  # 结果过期时间（1小时）
    task_acks_late=True,  # 任务完成后才确认
    worker_disable_rate_limits=True,  # 禁用速率限制
    task_compression='gzip',  # 使用gzip压缩任务消息
    result_compression='gzip',  # 使用gzip压缩结果
)

# 如果需要，可以在这里定义定时任务
# celery_app.conf.beat_schedule = {
#     'check-pending-tasks': {
#         'task': 'app.analysis.machine_learing.tasks.celery_tasks.check_and_execute_pending_tasks',
#         'schedule': 300.0,  # 每5分钟执行一次
#     },
# }