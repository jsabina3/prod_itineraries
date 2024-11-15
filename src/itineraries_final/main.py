#!/usr/bin/env python
import sys
import warnings

from itineraries_final.crew import ItinerariesFinal

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

#!/usr/bin/env python
import sys
from itineraries_final.crew import ItinerariesFinal

def run():
    """
    Run the crew.
    """
    inputs = {
        'code': 'HBFR34',
        'names': 'Javi,Raquel',
        'num_travelers': '2',
        'origin': 'Madrid',
        'destination': 'Paris',
        'hotel_name': 'Meliá Champs Elysees',
        'hotel_address': 'Champs Elysees',
        'flight_outward_arrival_time': '09:40',
        'breakfast_included': 'Yes',
        'flight_return_departure_time': '19:00',
        'ages': '24,24',
        'start_date': '2024-11-16',
        'end_date': '2024-11-18',
        'flight_data': 'Outward UX1091 departing at 7:05 from Madrid-Barajas and arriving at 9:40 at Paris Orly | Return UX1094 departing at 19:00 from Paris Orly and arriving at 21:40 at Madrid-Barajas'
    }
    ItinerariesFinal().crew().kickoff(inputs=inputs)


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
        'start_date': '2024-11-16',
        'end_date': '2024-11-18',
        'flight_data': 'Outward W46012 | Return W46013'
    }
    try:
        ItinerariesFinal().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ItinerariesFinal().crew().replay(task_id=sys.argv[1])

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
        'start_date': '2024-11-16',
        'end_date': '2024-11-18',
        'flight_data': 'Outward W46012 | Return W46013'
    }
    try:
        ItinerariesFinal().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

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