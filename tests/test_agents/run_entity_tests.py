#!/usr/bin/env python3
"""
Quick Entity Extraction Test Runner

Run specific test categories or all tests.

Usage:
    python tests/test_agents/run_entity_tests.py                    # Run all tests
    python tests/test_agents/run_entity_tests.py candidates         # Test candidates only
    python tests/test_agents/run_entity_tests.py companies          # Test companies only
    python tests/test_agents/run_entity_tests.py pipeline           # Test pipeline only
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_entity_extraction import (
    test_candidate_extraction,
    test_company_extraction, 
    test_complete_pipeline,
    run_all_tests,
    print_header
)


async def main():
    """Main entry point for quick testing"""
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type in ['candidate', 'candidates']:
            print_header("CANDIDATE EXTRACTION TESTS ONLY")
            results = await test_candidate_extraction()
            passed = sum(results)
            total = len(results)
            print(f"\n🎯 RESULT: {passed}/{total} candidate tests passed ({(passed/total)*100:.1f}%)")
            
        elif test_type in ['company', 'companies']:
            print_header("COMPANY EXTRACTION TESTS ONLY")
            results = await test_company_extraction()
            passed = sum(results)
            total = len(results)
            print(f"\n🎯 RESULT: {passed}/{total} company tests passed ({(passed/total)*100:.1f}%)")
            
        elif test_type in ['pipeline', 'integration']:
            print_header("PIPELINE INTEGRATION TESTS ONLY")
            results = await test_complete_pipeline()
            passed = sum(results)
            total = len(results)
            print(f"\n🎯 RESULT: {passed}/{total} pipeline tests passed ({(passed/total)*100:.1f}%)")
            
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Available options: candidates, companies, pipeline")
            sys.exit(1)
    else:
        # Run all tests
        await run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
