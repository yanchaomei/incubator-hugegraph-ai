# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import unittest
from unittest.mock import patch, MagicMock

from hugegraph_llm.operators.hugegraph_op.schema_manager import SchemaManager


class TestSchemaManager(unittest.TestCase):
    @patch('hugegraph_llm.operators.hugegraph_op.schema_manager.PyHugeClient')
    def setUp(self, mock_client_class):
        # Setup mock client
        self.mock_client = MagicMock()
        self.mock_schema = MagicMock()
        self.mock_client.schema.return_value = self.mock_schema
        mock_client_class.return_value = self.mock_client
        
        # Create SchemaManager instance
        self.graph_name = "test_graph"
        self.schema_manager = SchemaManager(self.graph_name)
        
        # Sample schema data for testing
        self.sample_schema = {
            "vertexlabels": [
                {
                    "id": 1,
                    "name": "person",
                    "properties": ["name", "age"],
                    "primary_keys": ["name"],
                    "nullable_keys": [],
                    "index_labels": []
                },
                {
                    "id": 2,
                    "name": "software",
                    "properties": ["name", "lang"],
                    "primary_keys": ["name"],
                    "nullable_keys": [],
                    "index_labels": []
                }
            ],
            "edgelabels": [
                {
                    "id": 3,
                    "name": "created",
                    "source_label": "person",
                    "target_label": "software",
                    "frequency": "SINGLE",
                    "properties": ["weight"],
                    "sort_keys": [],
                    "nullable_keys": [],
                    "index_labels": []
                },
                {
                    "id": 4,
                    "name": "knows",
                    "source_label": "person",
                    "target_label": "person",
                    "frequency": "SINGLE",
                    "properties": ["weight"],
                    "sort_keys": [],
                    "nullable_keys": [],
                    "index_labels": []
                }
            ]
        }
        
    def test_init(self):
        """Test initialization of SchemaManager class."""
        self.assertEqual(self.schema_manager.graph_name, self.graph_name)
        self.assertEqual(self.schema_manager.client, self.mock_client)
        self.assertEqual(self.schema_manager.schema, self.mock_schema)
        
    def test_simple_schema_with_full_schema(self):
        """Test simple_schema method with a full schema."""
        # Call the method
        simple_schema = self.schema_manager.simple_schema(self.sample_schema)
        
        # Verify the result
        self.assertIn("vertexlabels", simple_schema)
        self.assertIn("edgelabels", simple_schema)
        
        # Check vertex labels
        self.assertEqual(len(simple_schema["vertexlabels"]), 2)
        for vertex in simple_schema["vertexlabels"]:
            self.assertIn("id", vertex)
            self.assertIn("name", vertex)
            self.assertIn("properties", vertex)
            self.assertNotIn("primary_keys", vertex)
            self.assertNotIn("nullable_keys", vertex)
            self.assertNotIn("index_labels", vertex)
            
        # Check edge labels
        self.assertEqual(len(simple_schema["edgelabels"]), 2)
        for edge in simple_schema["edgelabels"]:
            self.assertIn("name", edge)
            self.assertIn("source_label", edge)
            self.assertIn("target_label", edge)
            self.assertIn("properties", edge)
            self.assertNotIn("id", edge)
            self.assertNotIn("frequency", edge)
            self.assertNotIn("sort_keys", edge)
            self.assertNotIn("nullable_keys", edge)
            self.assertNotIn("index_labels", edge)
            
    def test_simple_schema_with_empty_schema(self):
        """Test simple_schema method with an empty schema."""
        empty_schema = {}
        simple_schema = self.schema_manager.simple_schema(empty_schema)
        self.assertEqual(simple_schema, {})
        
    def test_simple_schema_with_partial_schema(self):
        """Test simple_schema method with a partial schema."""
        partial_schema = {
            "vertexlabels": [
                {
                    "id": 1,
                    "name": "person",
                    "properties": ["name", "age"]
                }
            ]
        }
        simple_schema = self.schema_manager.simple_schema(partial_schema)
        self.assertIn("vertexlabels", simple_schema)
        self.assertNotIn("edgelabels", simple_schema)
        self.assertEqual(len(simple_schema["vertexlabels"]), 1)
        
    @patch('hugegraph_llm.operators.hugegraph_op.schema_manager.PyHugeClient')
    def test_run_with_valid_schema(self, mock_client_class):
        """Test run method with a valid schema."""
        # Setup mock
        mock_client = MagicMock()
        mock_schema = MagicMock()
        mock_schema.getSchema.return_value = self.sample_schema
        mock_client.schema.return_value = mock_schema
        mock_client_class.return_value = mock_client
        
        # Create SchemaManager instance
        schema_manager = SchemaManager(self.graph_name)
        
        # Call the run method
        context = {}
        result = schema_manager.run(context)
        
        # Verify the result
        self.assertIn("schema", result)
        self.assertIn("simple_schema", result)
        self.assertEqual(result["schema"], self.sample_schema)
        
    @patch('hugegraph_llm.operators.hugegraph_op.schema_manager.PyHugeClient')
    def test_run_with_empty_schema(self, mock_client_class):
        """Test run method with an empty schema."""
        # Setup mock
        mock_client = MagicMock()
        mock_schema = MagicMock()
        mock_schema.getSchema.return_value = {"vertexlabels": [], "edgelabels": []}
        mock_client.schema.return_value = mock_schema
        mock_client_class.return_value = mock_client
        
        # Create SchemaManager instance
        schema_manager = SchemaManager(self.graph_name)
        
        # Call the run method and expect an exception
        with self.assertRaises(Exception) as context:
            schema_manager.run({})
            
        # Verify the exception message
        self.assertIn(f"Can not get {self.graph_name}'s schema from HugeGraph!", str(context.exception))
        
    @patch('hugegraph_llm.operators.hugegraph_op.schema_manager.PyHugeClient')
    def test_run_with_existing_context(self, mock_client_class):
        """Test run method with an existing context."""
        # Setup mock
        mock_client = MagicMock()
        mock_schema = MagicMock()
        mock_schema.getSchema.return_value = self.sample_schema
        mock_client.schema.return_value = mock_schema
        mock_client_class.return_value = mock_client
        
        # Create SchemaManager instance
        schema_manager = SchemaManager(self.graph_name)
        
        # Call the run method with an existing context
        existing_context = {"existing_key": "existing_value"}
        result = schema_manager.run(existing_context)
        
        # Verify the result
        self.assertIn("existing_key", result)
        self.assertEqual(result["existing_key"], "existing_value")
        self.assertIn("schema", result)
        self.assertIn("simple_schema", result)
        
    @patch('hugegraph_llm.operators.hugegraph_op.schema_manager.PyHugeClient')
    def test_run_with_none_context(self, mock_client_class):
        """Test run method with None context."""
        # Setup mock
        mock_client = MagicMock()
        mock_schema = MagicMock()
        mock_schema.getSchema.return_value = self.sample_schema
        mock_client.schema.return_value = mock_schema
        mock_client_class.return_value = mock_client
        
        # Create SchemaManager instance
        schema_manager = SchemaManager(self.graph_name)
        
        # Call the run method with None context
        result = schema_manager.run(None)
        
        # Verify the result
        self.assertIn("schema", result)
        self.assertIn("simple_schema", result)


if __name__ == "__main__":
    unittest.main() 