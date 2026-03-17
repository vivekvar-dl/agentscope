"""Basic example of using AgentScope with a simple mock agent."""

from agentscope import AgentScope
from agentscope.core.metrics import StepType


class MockAgent:
    """Simple mock agent for demonstration."""
    
    def run(self, input_text: str) -> str:
        """Execute the agent."""
        # Simulate some work
        import time
        time.sleep(0.5)
        
        return f"Processed: {input_text}"


def main():
    """Run basic example."""
    print("="  * 60)
    print("AgentScope Basic Example")
    print("=" * 60)
    print()
    
    # Create a mock agent
    agent = MockAgent()
    
    # Wrap with AgentScope
    with AgentScope(agent, 
                    project="examples",
                    name="mock-agent",
                    verbose=True) as scope:
        
        # Manually log some steps (since this is a mock agent)
        scope.log_step(
            StepType.THOUGHT,
            "Starting to process the request",
            tokens=50,
            model="gpt-3.5-turbo",
        )
        
        scope.log_step(
            StepType.TOOL_CALL,
            "Calling processing function",
            metadata={"tool_name": "processor", "success": True},
            tokens=20,
        )
        
        # Run the agent
        result = agent.run("Hello, AgentScope!")
        
        scope.log_step(
            StepType.DECISION,
            f"Completed with result: {result}",
            tokens=30,
        )
    
    # Print summary after execution
    print("\n" + "=" * 60)
    print("Execution Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Cost: ${scope.cost:.4f}")
    print(f"   Tokens: {scope.tokens}")
    print(f"   Duration: {scope.duration_seconds:.2f}s")
    print(f"   Tool Calls: {scope.total_tool_calls}")
    
    # Export trace
    scope.export("basic_example_trace.json")
    print("\n✅ Trace exported to basic_example_trace.json")


if __name__ == "__main__":
    main()
