import json
import os
import sys

# Ensure the root directory is in sys.path so we can import from graph
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.workflow import graph

def generate_cached_transcript():
    query = "What is the refund policy for hardware, and also open a ticket for my defective monitor."
    
    print(f"Running query: {query}")
    initial_state = {"raw_input": query}
    
    try:
        result = graph.invoke(initial_state)
        
        # We want to save the final answer and the trace
        output_data = {
            "query": query,
            "final_answer": result.get("final_answer", ""),
            "trace": result.get("trace", [])
        }
        
        os.makedirs(os.path.join("..", "data"), exist_ok=True)
        out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cached_transcript.json"))
        with open(out_path, "w") as f:
            json.dump(output_data, f, indent=2)
            
        print(f"Successfully generated {out_path}")
    except Exception as e:
        print(f"Error generating transcript: {e}")

if __name__ == "__main__":
    generate_cached_transcript()
