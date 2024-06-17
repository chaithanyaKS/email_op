from core.processor import Process
from core.processor.process_executor import ProcessExecutor
from core.processor.search_engine import SearchEngine


class GmailProcessor:
    def __init__(self) -> None:
        self._processes = []

    def add(self, process_dict: dict):
        process = Process()
        process.add(process_dict)
        self._processes.append(process)
        return self

    def execute(self, search_engine: SearchEngine, executor: ProcessExecutor):
        for process in self._processes:
            msg_ids = search_engine.search(process.rule)
            print(msg_ids)
            executor.execute(process.actions, msg_ids)
