import unittest
from unittest.mock import MagicMock, patch
import numpy as np

# Mock torch before importing worker
with patch.dict('sys.modules', {'torch': MagicMock(), 'torch.nn': MagicMock()}):
    from inference_worker import InferenceWorker

class TestInferenceWorker(unittest.TestCase):
    
    @patch('inference_worker.torch')
    def test_initialization(self, mock_torch):
        # Setup mocks
        mock_torch.cuda.is_available.return_value = False
        mock_torch.jit.load.return_value = MagicMock()
        
        worker = InferenceWorker(model_path="test_model.pt", device="cpu")
        
        self.assertIsNotNone(worker.model)
        self.assertEqual(worker.model_name, "test_model.pt")

    @patch('inference_worker.torch')
    def test_predict(self, mock_torch):
        # Setup mocks
        mock_model = MagicMock()
        mock_torch.jit.load.return_value = mock_model
        
        # Mock tensor conversion and model output
        mock_tensor = MagicMock()
        mock_torch.tensor.return_value = mock_tensor
        
        # Mock model output (return a mocked tensor)
        mock_output = MagicMock()
        mock_output.cpu().numpy().tolist.return_value = [[0.1, 0.9]]
        mock_model.return_value = mock_output
        
        worker = InferenceWorker(model_path="test.pt", device="cpu")
        
        # Test input
        inputs = [np.zeros((3, 224, 224))]
        results = worker.predict(inputs)
        
        self.assertEqual(len(results), 1)
        self.assertIn("prediction", results[0])
        self.assertIn("latency_ms", results[0])
        self.assertEqual(results[0]["prediction"], [[0.1, 0.9]])

if __name__ == '__main__':
    unittest.main()
