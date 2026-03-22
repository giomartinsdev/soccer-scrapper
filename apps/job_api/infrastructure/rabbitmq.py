"""RabbitMQ job queue implementation."""

from typing import Dict

import aio_pika
from aio_pika import Message, DeliveryMode

from apps.common.logging import setup_logging
from apps.job_api.application.ports import JobQueuePort
from apps.job_api.config import settings
from apps.job_api.domain.entities import Job


logger = setup_logging(__name__)


class RabbitMQJobQueue(JobQueuePort):
    """RabbitMQ implementation of job queue port."""

    _connection: aio_pika.RobustConnection = None
    _channel: aio_pika.Channel = None

    @classmethod
    async def connect(cls):
        """Connect to RabbitMQ."""
        if cls._connection is None:
            cls._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            cls._channel = await cls._connection.channel()

            await cls._channel.declare_queue(
                settings.job_queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": 86400000,
                },
            )

            logger.info(f"Connected to RabbitMQ, queue: {settings.job_queue_name}")

    @classmethod
    async def disconnect(cls):
        """Disconnect from RabbitMQ."""
        if cls._connection:
            await cls._connection.close()
            cls._connection = None
            cls._channel = None
            logger.info("Disconnected from RabbitMQ")

    def publish_job(self, job: Job) -> None:
        """Publish job to queue."""
        import asyncio
        from aio_pika import Message

        if self._channel is None:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.connect())

        task_map = {
            "leagues": "scrap.leagues",
            "teams": "scrap.teams",
            "events": "scrap.events",
            "live": "scrap.live",
            "predictions": "scrap.predictions",
        }

        task_name = task_map.get(job.endpoint, "scrap.generic")

        message_body = {
            "job_id": job.id,
            "endpoint": job.endpoint,
            "params": job.params,
        }

        message = Message(
            body=str(message_body).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._channel.default_exchange.publish(
                message, routing_key=settings.job_queue_name
            )
        )

        logger.info(f"Published job {job.id} to queue with task {task_name}")

    async def publish_job_async(self, job: Job) -> None:
        """Async publish job to queue."""
        if self._channel is None:
            await self.connect()

        task_map = {
            "leagues": "scrap.leagues",
            "teams": "scrap.teams",
            "events": "scrap.events",
            "live": "scrap.live",
            "predictions": "scrap.predictions",
        }

        task_name = task_map.get(job.endpoint, "scrap.generic")

        message_body = {
            "job_id": job.id,
            "endpoint": job.endpoint,
            "params": job.params,
        }

        message = Message(
            body=str(message_body).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        await self._channel.default_exchange.publish(
            message, routing_key=settings.job_queue_name
        )

        logger.info(f"Published job {job.id} to queue with task {task_name}")
