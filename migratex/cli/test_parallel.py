"""
CLI command for parallel test execution
"""

import click
from pathlib import Path
from migratex.testing.parallel_agents import ParallelTestOrchestrator, TestAgentFactory
from migratex.testing.results_tracker import testing_tracker


@click.command("test-parallel")
@click.option("--test-dir", type=click.Path(path_type=Path), default=Path("tests"),
              help="Directory containing tests")
@click.option("--num-agents", type=int, default=None,
              help="Number of parallel agents (default: CPU count, max 8)")
@click.option("--mode", type=click.Choice(["process", "thread"]), default="process",
              help="Execution mode: process (default) or thread")
@click.option("--category", type=click.Choice(["unit", "integration", "e2e", "edge_case", "outlier", "performance", "all"]),
              default="all", help="Test category to run")
@click.option("--output", type=click.Path(path_type=Path), default=Path("parallel-test-results.json"),
              help="Output file for results")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def test_parallel_command(
    test_dir: Path,
    num_agents: int | None,
    mode: str,
    category: str,
    output: Path,
    verbose: bool
):
    """
    Run tests in parallel using multiple testing agents.
    
    Distributes tests across multiple agents for faster execution.
    """
    click.echo(f"Running parallel tests from: {test_dir}")
    click.echo(f"Execution mode: {mode}")
    
    if category == "all":
        # Run all tests in parallel
        orchestrator = ParallelTestOrchestrator(
            test_dir=test_dir,
            num_agents=num_agents,
            execution_mode=mode
        )
        
        click.echo(f"Starting {orchestrator.num_agents} parallel test agents...")
        summary = orchestrator.run_parallel()
        
        # Save results
        orchestrator.save_results(output)
        
        # Display summary
        click.echo("\n" + "="*60)
        click.echo("PARALLEL TEST EXECUTION SUMMARY")
        click.echo("="*60)
        click.echo(f"Agents: {summary['num_agents']}")
        click.echo(f"Tests Run: {summary['total_tests_run']}")
        click.echo(f"Tests Passed: {summary['total_tests_passed']}")
        click.echo(f"Tests Failed: {summary['total_tests_failed']}")
        click.echo(f"Success Rate: {summary['success_rate']:.1f}%")
        click.echo(f"Agents Completed: {summary['agents_completed']}")
        click.echo(f"Agents Failed: {summary['agents_failed']}")
        click.echo(f"Overall Status: {summary['overall_status'].upper()}")
        click.echo("="*60)
        click.echo(f"\nResults saved to: {output}")
        
        if summary['overall_status'] == "failed":
            click.echo("\n✗ Some tests failed. Check results for details.", err=True)
            raise click.Abort()
        else:
            click.echo("\n✓ All tests passed!")
    
    else:
        # Run specific category
        factory = TestAgentFactory()
        tracker = testing_tracker
        
        agent_map = {
            "unit": factory.create_unit_test_agent,
            "integration": factory.create_integration_test_agent,
            "e2e": factory.create_e2e_test_agent,
            "edge_case": factory.create_edge_case_test_agent,
            "outlier": factory.create_outlier_test_agent,
            "performance": factory.create_performance_test_agent,
        }
        
        if category not in agent_map:
            click.echo(f"Unknown category: {category}", err=True)
            raise click.Abort()
        
        agent = agent_map[category](test_dir, tracker)
        click.echo(f"Running {category} tests...")
        result = agent.run()
        
        click.echo(f"\n{category.upper()} Test Results:")
        click.echo(f"  Tests Run: {result.get('tests_run', 0)}")
        click.echo(f"  Tests Passed: {result.get('tests_passed', 0)}")
        click.echo(f"  Tests Failed: {result.get('tests_failed', 0)}")
        click.echo(f"  Status: {result.get('status', 'unknown').upper()}")
        
        if result.get('status') != 'completed':
            click.echo("\n✗ Tests failed.", err=True)
            raise click.Abort()

