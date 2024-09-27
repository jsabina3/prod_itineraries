from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from itinerary_dev_crew.tools.serper_tool import CustomSerperDevTool
from itinerary_dev_crew.tools.accuweather_tool import AccuWeatherTool
from itinerary_dev_crew.tools.exasearch_tool import ExaSearchTool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class ItineraryDevCrewCrew():
	"""ItineraryDevCrew crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def research_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['research_agent'],
			tools=[ExaSearchTool(), CustomSerperDevTool(), AccuWeatherTool()],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o-mini', temperature=0.05)
		)

	@agent
	def itinerary_developer(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_developer'],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o-mini', temperature=0.1)
		)

	@agent
	def itinerary_geographical_expert(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_geographical_expert'],
			tools=[CustomSerperDevTool()],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o-mini', temperature=0)
		)

	@agent
	def itinerary_translator_and_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_translator_and_writer'],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o-2024-08-06', temperature=0.15)
		)

	@agent
	def PR_director(self) -> Agent:
		return Agent(
			config=self.agents_config['PR_director'],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o-2024-08-06', temperature=0.15)
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.research_agent()
		)

	@task
	def itinerary_task(self) -> Task:
		return Task(
			config=self.tasks_config['itinerary_task'],
			agent=self.itinerary_developer()
		)

	@task
	def itinerary_geo_organization(self) -> Task:
		return Task(
			config=self.tasks_config['itinerary_geo_organization'],
			agent=self.itinerary_geographical_expert()
		)

	@task
	def itinerary_translation_and_writing(self) -> Task:
		return Task(
			config=self.tasks_config['itinerary_translation_and_writing'],
			agent=self.itinerary_translator_and_writer()
		)

	@task
	def PR_adaptation(self) -> Task:
		return Task(
			config=self.tasks_config['PR_adaptation'],
			agent=self.PR_director()
		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents,  # Automatically created by the @agent decorator
			tasks=self.tasks,  # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=False,
			memory=False
		)