#!/usr/bin/env python
import sys
from business_automation_introduction.crew import BusinessAutomationIntroductionCrew

def run():
    """
    Run the crew.
    """
    inputs = {
        'names': 'Javi,Raquel',
        'num_travelers': '2',
        'origin': 'Madrid',
        'destination': 'Paris',
        'hotel_name': 'Melia Champs Elysees',
        'hotel_address': 'Champs Elysees',
        'flight_outward_arrival_time': '12:10',
        'breakfast_included': 'Yes',
        'flight_return_departure_time': '19:00',
        'ages': '24,24',
        'start_date': '2024-11-01',
        'end_date': '2024-11-03',
        'flight_data': 'Outward W46012 | Return W46013'
    }
    BusinessAutomationIntroductionCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'names': 'Javi,Raquel',
        'num_travelers': '2',
        'origin': 'Madrid',
        'destination': 'Paris',
        'hotel_name': 'Melia Champs Elysees',
        'hotel_address': 'Champs Elysees',
        'flight_outward_arrival_time': '12:10',
        'breakfast_included': 'Yes',
        'flight_return_departure_time': '19:00',
        'ages': '24,24',
        'start_date': '2024-11-01',
        'end_date': '2024-11-03',
        'flight_data': 'Outward W46012 | Return W46013'
    }
    try:
        BusinessAutomationIntroductionCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        BusinessAutomationIntroductionCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'names': 'Javi,Raquel',
        'num_travelers': '2',
        'origin': 'Madrid',
        'destination': 'Paris',
        'hotel_name': 'Melia Champs Elysees',
        'hotel_address': 'Champs Elysees',
        'flight_outward_arrival_time': '12:10',
        'breakfast_included': 'Yes',
        'flight_return_departure_time': '19:00',
        'ages': '24,24',
        'start_date': '2024-11-01',
        'end_date': '2024-11-03',
        'flight_data': 'Outward W46012 | Return W46013'
    }
    try:
        BusinessAutomationIntroductionCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)