#!/usr/bin/env python3
"""
Boolean Query Processor Test
Demonstrates all Boolean operations and wildcard matching
"""

from tree23 import boolean_model

def run_tests():
    """Run comprehensive tests"""
    print("🔍 BOOLEAN QUERY PROCESSOR TEST")
    print("=" * 50)
    
    # Initialize documents
    doc1 = """At very low temperatures, superconductors have zero resistance, 
              but they can also repel an external magnetic field, in such a way 
              that a spinning magnet can be held in a levitated position."""
    
    doc2 = """If a small magnet is brought near a superconductor, 
              it will be repelled."""
    
    # Create boolean model
    bm = boolean_model()
    bm.add_document("Doc1", doc1)
    bm.add_document("Doc2", doc2)
    
    print("✅ Documents loaded successfully!")
    print("📄 Doc1: About superconductors and magnetic fields")
    print("📄 Doc2: About magnets and superconductors")
    print()
    
    # Test queries
    test_queries = [
        # Single terms
        ("superconductor", "Single term"),
        ("magnet", "Single term"),
        ("temperatures", "Single term"),
        
        # Wildcards
        ("super*", "Wildcard - prefix"),
        ("*magnet*", "Wildcard - contains"),
        ("*ed", "Wildcard - suffix"),
        ("temp*", "Wildcard - prefix"),
        
        # Boolean operations
        ("superconductor AND magnet", "AND operation"),
        ("superconductor OR magnet", "OR operation"),
        ("superconductor NOT magnet", "NOT operation"),
        ("superconductor XOR magnet", "XOR operation"),
        ("superconductor AND NOT magnet", "AND NOT operation"),
        ("superconductor OR NOT magnet", "OR NOT operation"),
        
        # Complex queries
        ("temperatures AND field", "AND with different terms"),
        ("resistance OR repelled", "OR with different terms"),
        ("super* AND magnet", "Wildcard + Boolean"),
        ("temp* OR field", "Wildcard + Boolean"),
    ]
    
    print("🧪 Running tests:")
    print("-" * 30)
    
    for i, (query, description) in enumerate(test_queries, 1):
        result = bm.boolean_query(query)
        print(f"{i:2d}. {description}")
        print(f"    Query: '{query}'")
        print(f"    Result: {result}")
        print()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    run_tests()
