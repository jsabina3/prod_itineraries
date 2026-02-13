from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from itineraries_final.tools.openweather_tool import OpenWeatherTool
from itineraries_final.tools.viator_activity_tool import ViatorTopProductsTool
from itineraries_final.tools.distance_matrix_tool import LocationStatusDistanceTool
from itineraries_final.tools.perplexity_tool import RealTimeSearchTool

@CrewBase
class ItinerariesFinal():
    """Waynabox travel itinerary generation crew"""

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            allow_delegation=False,
            max_iter=10,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', temperature=0.05)
        )

    @agent
    def research_agent_viator(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent_viator'],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', temperature=0.05)
        )

    @agent
    def research_agent_weather(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent_weather'],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', temperature=0.05)
        )

    @agent
    def research_agent_web(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent_web'],
            verbose=True,
            allow_delegation=False,
            max_iter=8,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', temperature=0.05)
        )

    @agent
    def itinerary_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_developer'],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', reasoning_effort='medium')
        )

    @agent
    def itinerary_translator_and_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_translator_and_writer'],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', reasoning_effort='medium')
        )

    @agent
    def PR_director(self) -> Agent:
        return Agent(
            config=self.agents_config['PR_director'],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', reasoning_effort='medium')
        )

    @agent
    def Itinerary_Director(self) -> Agent:
        return Agent(
            config=self.agents_config['Itinerary_Director'],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_retry_limit=2,
            llm=LLM(model='gpt-5.2', reasoning_effort='medium')
        )

    @task
    def gather_viator_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['gather_viator_data_task'],
            tools=[ViatorTopProductsTool()],
        )

    @task
    def fetch_weather_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_weather_data_task'],
            tools=[OpenWeatherTool()],
        )

    @task
    def web_search_additional_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_search_additional_research_task'],
            tools=[RealTimeSearchTool()],
        )

    @task
    def date_specific_events_task(self) -> Task:
        return Task(
            config=self.tasks_config['date_specific_events_task'],
            tools=[RealTimeSearchTool()],
        )

    @task
    def itinerary_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_task'],
        )

    @task
    def directions_task(self) -> Task:
        return Task(
            config=self.tasks_config['directions_task'],
            tools=[LocationStatusDistanceTool()],
        )

    @task
    def itinerary_translation_and_writing(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_translation_and_writing'],
        )

    @task
    def PR_adaptation(self) -> Task:
        return Task(
            config=self.tasks_config['PR_adaptation'],
        )

    @task
    def Itinerary_Curation(self) -> Task:
        return Task(
            config=self.tasks_config['Itinerary_Curation'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Waynabox itinerary generation crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=False,
            cache=True
        )
