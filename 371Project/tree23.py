import re

class Node23:
    """Node in a 2-3 tree"""
    def __init__(self):
        self.keys = []  # 1 or 2 keys (terms)
        self.posting_lists = []  # Corresponding posting lists
        self.children = []  # 0, 2, or 3 children
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def is_full(self):
        return len(self.keys) == 2
    
    def insert_in_node(self, key, posting_list):
        """Insert key in sorted order within node"""
        i = 0
        while i < len(self.keys) and key > self.keys[i]:
            i += 1
        self.keys.insert(i, key)
        self.posting_lists.insert(i, posting_list)

class Tree23InvertedIndex:
    def __init__(self):
        self.root = Node23()
        self.stop_words = {'a', 'an', 'the', 'in', 'is', 'it', 'that', 'they', 
                           'can', 'be', 'will', 'but', 'such', 'also', 'have',
                           'if', 'at', 'to', 'as'}
    
    def tokenize(self, text):
        text = text.lower()
        tokens = re.findall(r'\b[a-z]+\b', text)
        return tokens
    
    def normalize(self, tokens):
        return [token for token in tokens if token not in self.stop_words]
    
    def search(self, term):
        """Search for a term and return its posting list"""
        return self._search_recursive(self.root, term)
    
    def _search_recursive(self, node, term):
        """Recursive search in 2-3 tree"""
        if node is None:
            return []
        
        # Check keys in current node
        for i, key in enumerate(node.keys):
            if term == key:
                return node.posting_lists[i]
        
        # If leaf and not found
        if node.is_leaf():
            return []
        
        # Find appropriate child to search
        if term < node.keys[0]:
            return self._search_recursive(node.children[0], term)
        elif len(node.keys) == 1 or term < node.keys[1]:
            return self._search_recursive(node.children[1], term)
        else:
            return self._search_recursive(node.children[2], term)
    
    def insert(self, term, doc_id):
        """Insert term into 2-3 tree"""
        # Check if term already exists
        existing = self.search(term)
        if existing:
            # Term exists, update posting list
            self._update_posting_list(self.root, term, doc_id)
        else:
            # New term, insert it
            result = self._insert_recursive(self.root, term, [doc_id])
            if result is not None:  # Root split
                new_root = Node23()
                new_root.keys = [result[1]]
                new_root.posting_lists = [result[3]]  # Use the actual posting list
                new_root.children = [result[0], result[2]]
                self.root = new_root
    
    def _update_posting_list(self, node, term, doc_id):
        """Update posting list for existing term"""
        for i, key in enumerate(node.keys):
            if term == key:
                if doc_id not in node.posting_lists[i]:
                    node.posting_lists[i].append(doc_id)
                return True
        
        if not node.is_leaf():
            if term < node.keys[0]:
                return self._update_posting_list(node.children[0], term, doc_id)
            elif len(node.keys) == 1 or term < node.keys[1]:
                return self._update_posting_list(node.children[1], term, doc_id)
            else:
                return self._update_posting_list(node.children[2], term, doc_id)
    
    def _insert_recursive(self, node, term, posting_list):
        """Recursive insertion with node splitting"""
        if node.is_leaf():
            if not node.is_full():
                node.insert_in_node(term, posting_list)
                return None
            else:
                # Split leaf node
                return self._split_node(node, term, posting_list, None)
        
        # Find child to insert into
        if term < node.keys[0]:
            child_idx = 0
        elif len(node.keys) == 1 or term < node.keys[1]:
            child_idx = 1
        else:
            child_idx = 2
        
        result = self._insert_recursive(node.children[child_idx], term, posting_list)
        
        if result is None:
            return None
        
        # Child split, need to insert middle value
        if not node.is_full():
            node.insert_in_node(result[1], result[3])
            node.children[child_idx] = result[0]
            node.children.insert(child_idx + 1, result[2])
            return None
        else:
            return self._split_node(node, result[1], result[3], result)
    
    def _split_node(self, node, new_key, new_posting, split_result):
        """Split a full node"""
        # Temporarily add new key
        temp_keys = node.keys + [new_key]
        temp_postings = node.posting_lists + [new_posting]
        temp_children = node.children[:]
        
        if split_result:
            # Insert split children
            for i, key in enumerate(temp_keys[:-1]):
                if new_key < key or (i == len(temp_keys) - 2):
                    idx = i if new_key < key else i + 1
                    temp_children[idx] = split_result[0]
                    temp_children.insert(idx + 1, split_result[2])
                    break
        
        # Sort
        sorted_pairs = sorted(zip(temp_keys, temp_postings))
        temp_keys = [k for k, _ in sorted_pairs]
        temp_postings = [p for _, p in sorted_pairs]
        
        # Create two new nodes
        left = Node23()
        left.keys = [temp_keys[0]]
        left.posting_lists = [temp_postings[0]]
        
        right = Node23()
        right.keys = [temp_keys[2]]
        right.posting_lists = [temp_postings[2]]
        
        if temp_children:
            left.children = temp_children[:2]
            right.children = temp_children[2:]
        
        return (left, temp_keys[1], right, temp_postings[1])
    
    def wildcard_search(self, pattern):
        """Search with wildcard"""
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            results = []
            self._collect_with_prefix(self.root, prefix, results)
            return results
        return []
    
    def _collect_with_prefix(self, node, prefix, results):
        """Collect all terms starting with prefix"""
        if node is None:
            return
        
        for i, key in enumerate(node.keys):
            if key.startswith(prefix):
                results.append((key, node.posting_lists[i]))
        
        if not node.is_leaf():
            for child in node.children:
                self._collect_with_prefix(child, prefix, results)
    
    def add_document(self, doc_id, text):
        """Add document to index"""
        tokens = self.tokenize(text)
        terms = self.normalize(tokens)
        
        for term in terms:
            self.insert(term, doc_id)
    
    def display_index(self):
        """Display the index"""
        print("\n=== INVERTED INDEX (2-3 Tree) ===")
        terms = []
        self._collect_all_terms(self.root, terms)
        terms.sort()
        for term, posting_list in terms:
            docs = ', '.join(posting_list)
            print(f"{term} → [{docs}]")
    
    def _collect_all_terms(self, node, terms):
        """Collect all terms from tree"""
        if node is None:
            return
        
        for i, key in enumerate(node.keys):
            terms.append((key, node.posting_lists[i]))
        
        if not node.is_leaf():
            for child in node.children:
                self._collect_all_terms(child, terms)


class PermutermIndex:
    """Permuterm index for wildcard matching"""
    def __init__(self):
        self.permuterms = {}  # permuterm -> original_term
    
    def add_term(self, term):
        """Add all rotations of a term to the permuterm index"""
        # Add the term with $ marker
        term_with_marker = term + '$'
        
        # Add all rotations
        for i in range(len(term_with_marker)):
            rotation = term_with_marker[i:] + term_with_marker[:i]
            self.permuterms[rotation] = term
    
    def wildcard_search(self, pattern):
        """Search for terms matching wildcard pattern"""
        if '*' not in pattern:
            return [pattern] if pattern in self.permuterms.values() else []
        
        # Convert pattern to permuterm query
        if pattern.endswith('*'):
            # Prefix query: comp* -> comp$
            query = pattern[:-1] + '$'
        elif pattern.startswith('*'):
            # Suffix query: *puter -> uter$
            query = pattern[1:] + '$'
        else:
            # Contains query: *put* -> put$*
            parts = pattern.split('*')
            if len(parts) == 2:
                query = parts[1] + '$' + parts[0]
            else:
                return []
        
        # Find matching terms
        matches = []
        for permuterm, original_term in self.permuterms.items():
            if permuterm.startswith(query):
                if original_term not in matches:
                    matches.append(original_term)
        
        # If no matches found with startswith, try alternative approach for prefix queries
        if not matches and pattern.endswith('*'):
            prefix = pattern[:-1]
            for permuterm, original_term in self.permuterms.items():
                if permuterm.startswith(prefix) and permuterm.endswith('$'):
                    if original_term not in matches:
                        matches.append(original_term)
        
        return matches


class boolean_model:
    """Boolean query processor with inverted index and permuterm index"""
    
    def __init__(self):
        self.inverted_index = Tree23InvertedIndex()
        self.permuterm_index = PermutermIndex()
        self.documents = {}  # doc_id -> document text
        self.all_doc_ids = set()
    
    def add_document(self, doc_id, text):
        """Add document to both indices"""
        self.documents[doc_id] = text
        self.all_doc_ids.add(doc_id)
        
        # Add to inverted index
        self.inverted_index.add_document(doc_id, text)
        
        # Add terms to permuterm index
        tokens = self.inverted_index.tokenize(text)
        terms = self.inverted_index.normalize(tokens)
        for term in set(terms):  # Remove duplicates
            self.permuterm_index.add_term(term)
    
    def _get_posting_list(self, term):
        """Get posting list for a term, handling wildcards"""
        if '*' in term:
            # Handle wildcard
            matching_terms = self.permuterm_index.wildcard_search(term)
            all_docs = set()
            for matching_term in matching_terms:
                docs = self.inverted_index.search(matching_term)
                all_docs.update(docs)
            return list(all_docs)
        else:
            return self.inverted_index.search(term)
    
    def _and_operation(self, list1, list2):
        """AND operation: intersection of two posting lists"""
        return list(set(list1) & set(list2))
    
    def _or_operation(self, list1, list2):
        """OR operation: union of two posting lists"""
        return list(set(list1) | set(list2))
    
    def _not_operation(self, list1):
        """NOT operation: all documents not in the list"""
        return list(self.all_doc_ids - set(list1))
    
    def _xor_operation(self, list1, list2):
        """XOR operation: documents in exactly one of the lists"""
        set1, set2 = set(list1), set(list2)
        return list((set1 - set2) | (set2 - set1))
    
    def _and_not_operation(self, list1, list2):
        """AND NOT operation: documents in list1 but not in list2"""
        return list(set(list1) - set(list2))
    
    def _or_not_operation(self, list1, list2):
        """OR NOT operation: documents in list1 or not in list2"""
        return list(set(list1) | (self.all_doc_ids - set(list2)))
    
    def boolean_query(self, query):
        """
        Process Boolean query with up to two terms and one operator
        Supported operators: AND, OR, NOT, XOR, AND NOT, OR NOT
        """
        import re
        query = query.strip()
        
        # Handle single term (no operator)
        if not any(re.search(r'\b' + op.strip() + r'\b', query.upper()) for op in [' AND ', ' OR ', ' NOT ', ' XOR ', ' AND NOT ', ' OR NOT ']):
            return self._get_posting_list(query)
        
        # Parse query to find operator and terms using regex
        operators = [
            (r'\bAND NOT\b', ' AND NOT '),
            (r'\bOR NOT\b', ' OR NOT '),
            (r'\bAND\b', ' AND '),
            (r'\bOR\b', ' OR '),
            (r'\bXOR\b', ' XOR '),
            (r'\bNOT\b', ' NOT ')
        ]
        
        for pattern, op in operators:
            match = re.search(pattern, query.upper())
            if match:
                # Split the query at the operator position
                parts = re.split(pattern, query.upper(), maxsplit=1)
                if len(parts) == 2:
                    # Get original case terms
                    original_parts = re.split(pattern, query, maxsplit=1)
                    if len(original_parts) == 2:
                        term1 = original_parts[0].strip()
                        term2 = original_parts[1].strip()
                    else:
                        term1 = parts[0].strip()
                        term2 = parts[1].strip()
                    
                    # Get posting lists
                    list1 = self._get_posting_list(term1)
                    
                    if op == ' NOT ':
                        # NOT operation (unary)
                        return self._not_operation(list1)
                    else:
                        # Binary operations
                        list2 = self._get_posting_list(term2)
                        
                        if op == ' AND ':
                            return self._and_operation(list1, list2)
                        elif op == ' OR ':
                            return self._or_operation(list1, list2)
                        elif op == ' XOR ':
                            return self._xor_operation(list1, list2)
                        elif op == ' AND NOT ':
                            return self._and_not_operation(list1, list2)
                        elif op == ' OR NOT ':
                            return self._or_not_operation(list1, list2)
        
        return []  # Invalid query format
    
    def display_index(self):
        """Display the inverted index"""
        self.inverted_index.display_index()
    
    def display_permuterm_index(self):
        """Display the permuterm index"""
        print("\n=== PERMUTERM INDEX ===")
        for permuterm, original in sorted(self.permuterm_index.permuterms.items()):
            print(f"{permuterm} -> {original}")


# Main execution
if __name__ == "__main__":
    # Initialize the documents
    doc1 = """At very low temperatures, superconductors have zero resistance, 
              but they can also repel an external magnetic field, in such a way 
              that a spinning magnet can be held in a levitated position."""
    
    doc2 = """If a small magnet is brought near a superconductor, 
              it will be repelled."""
    
    # Create boolean model and add documents
    bm = boolean_model()
    bm.add_document("Doc1", doc1)
    bm.add_document("Doc2", doc2)
    
    # Display indices
    bm.display_index()
    bm.display_permuterm_index()
    
    # Test queries
    print("\n=== BOOLEAN QUERY TESTS ===")
    
    test_queries = [
        "superconductor",
        "magnet",
        "super*",
        "superconductor AND magnet",
        "superconductor OR magnet", 
        "superconductor NOT magnet",
        "superconductor XOR magnet",
        "superconductor AND NOT magnet",
        "superconductor OR NOT magnet",
        "temperatures AND field",
        "resistance OR repelled",
        "levitated NOT small"
    ]
    
    for query in test_queries:
        result = bm.boolean_query(query)
        print(f"Query: '{query}' -> {result}")