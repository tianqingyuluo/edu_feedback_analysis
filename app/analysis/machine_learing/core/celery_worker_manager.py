import multiprocessing
import signal
import sys
import traceback

from app.core.logging import app_logger


class CeleryWorkerManager:
    def __init__(self):
        self.worker_process: multiprocessing.Process | None = None
        self.worker_stopped = multiprocessing.Event()

    def start_worker(self):
        """启动 Celery Worker 进程"""
        if self.worker_process and self.worker_process.is_alive():
            app_logger.warning("Celery Worker 已经在运行")
            return

        self.worker_stopped.clear()
        self.worker_process = multiprocessing.Process(
            target=self._run_worker, daemon=False
        )
        self.worker_process.start()
        app_logger.info(f"Celery Worker 进程已启动，PID: {self.worker_process.pid}")

    def stop_worker(self):
        """停止 Celery Worker 进程"""
        if not self.worker_process or not self.worker_process.is_alive():
            app_logger.warning("Celery Worker 未运行")
            return

        self.worker_stopped.set()

        # 发送 SIGTERM 信号给 Worker 进程
        self.worker_process.terminate()

        # 等待进程结束
        self.worker_process.join(timeout=5)

        if self.worker_process.is_alive():
            app_logger.warning("Celery Worker 未正常终止，强制结束")
            self.worker_process.kill()

        app_logger.info("Celery Worker 进程已停止")

    def _run_worker(self):
        """运行 Celery Worker 的目标函数"""
        try:
            # 导入 Celery 应用
            from app.core.celery_app import celery_app

            # 设置信号处理
            def signal_handler(signum, frame):
                app_logger.info(f"收到信号 {signum}，正在停止 Celery Worker")
                sys.exit(0)

            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

            # 启动 Celery Worker
            argv = [
                "worker",
                "--loglevel=info",
                "-P",
                "solo",
                "-c",
                "1",
                "--max-tasks-per-child=1",
                "--time-limit=3600",
                "--soft-time-limit=3300",
            ]

            app_logger.info("启动 Celery Worker")
            celery_app.worker_main(argv)

        except Exception as e:
            app_logger.error(f"Celery Worker 进程出错: {str(e)}")
            app_logger.error(f"详情:{traceback.format_exc()}")
            sys.exit(1)