from __future__ import annotations

from typing import Dict, Optional, Union

from google.cloud.logging_v2.client import Client
from google.cloud.logging_v2.resource import Resource
from strivelogger.logger_implementation import LoggerImplementation


class StackDriverLogger(LoggerImplementation):
    def __init__(self, project_id, service_name, region):
        self.client = Client(project=project_id)
        self.project_id = project_id
        self.service_name = service_name
        self.region = region

    def __get_resource(self):
        return Resource(
            type="cloud_run_revision",
            labels={
                "project_id": self.project_id,
                "service_name": self.service_name,
                "location": self.region,
            },
        )

    def __log(
        self,
        severity: str,
        message: str,
        trace_id: Optional[str],
        extra: Dict = None,
        exc_info=None,
    ):
        if extra or exc_info:
            struct = {"message": message}

            if extra:
                struct["extra"] = extra

            if exc_info:
                struct["exception"] = exc_info
                struct["serviceContext"] = {"service": self.service_name}
                struct["@type"] = "type.googleapis.com/google.devtools.clouderrorreporting.v1beta1.ReportedErrorEvent"

            self.client.logger(self.service_name).log_struct(
                struct,
                severity=severity,
                resource=self.__get_resource(),
                trace=trace_id,
            )
        else:
            self.client.logger(self.service_name).log_text(
                message,
                severity=severity,
                resource=self.__get_resource(),
                trace=trace_id,
            )

    def debug(self, message: str, trace_id: Optional[str], extra: Dict = None):
        self.__log("DEBUG", message, trace_id=trace_id, extra=extra)

    def info(self, message: str, trace_id: Optional[str], extra: Dict = None):
        self.__log("INFO", message, trace_id=trace_id, extra=extra)

    def warn(self, message: str, trace_id: Optional[str], extra: Dict = None):
        self.__log("WARNING", message, trace_id=trace_id, extra=extra)

    def error(
        self,
        message: str,
        trace_id: Optional[str],
        exc_info: Optional[Union[BaseException, str]],
        extra: Optional[Dict],
    ):
        self.__log("ERROR", message, extra=extra, trace_id=trace_id, exc_info=exc_info)
