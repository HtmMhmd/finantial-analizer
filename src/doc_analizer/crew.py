from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from doc_analizer.tools import LandingAIDocumentExtractor

from . import llm

@CrewBase
class DocAnalizer():
    """DocAnalizer crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def document_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['document_extractor'], # type: ignore[index]
            verbose=True,
            tools=[LandingAIDocumentExtractor()],
        )
    
    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'], # type: ignore[index]
            verbose=True
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'], # type: ignore[index]
            verbose=True
        )

    @task
    def extract_documents(self) -> Task:
        return Task(
            config=self.tasks_config['extract_documents'], # type: ignore[index]
            verbose=True
        )
    @task
    def analyze_financial_data(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_financial_data'], # type: ignore[index]
            verbose=True
        )
    @task
    def generate_report(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report'], # type: ignore[index]
            verbose=True
        )
    
    @tool
    def landing_ai_document_extractor(self) -> LandingAIDocumentExtractor:
        return LandingAIDocumentExtractor()

    @crew
    def crew(self) -> Crew:
        """Creates the DocAnalizer crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )


#TODO : add calculator tool also add visualization tool maybe matplotlib and seaborn also add tool for email reporting