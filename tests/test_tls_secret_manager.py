"""Exercise Secret Manager TLS wiring without ADC lookup or API traffic."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import certifi
from google.auth.credentials import AnonymousCredentials

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("secret_manager_under_test", ROOT / "src/tools/secret_manager.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SecretManagerTLSTests(unittest.TestCase):
    def test_explicit_patched_roots_and_existing_credentials(self):
        credentials = AnonymousCredentials()
        transport_type = module.SecretManagerServiceGrpcTransport
        response = SimpleNamespace(payload=SimpleNamespace(data=b"test-secret"))
        with patch("google.auth.default", return_value=(credentials, "test-project")), \
             patch.object(transport_type, "create_channel", return_value=MagicMock()), \
             patch.object(module.grpc, "ssl_channel_credentials", wraps=module.grpc.ssl_channel_credentials) as tls, \
             patch.object(module, "SecretManagerServiceGrpcTransport", wraps=transport_type) as transport, \
             patch.object(module.secretmanager.SecretManagerServiceClient, "access_secret_version", return_value=response) as access:
            manager = module.SecretManager()
            manager.get_secret_data("test-key")
            self.assertEqual(manager.data, ["test-secret"])
            tls.assert_called_once_with(root_certificates=Path(certifi.where()).read_bytes())
            access.assert_called_once_with(request={"name": "projects/test-project/secrets/test-key/versions/latest"})
            self.assertIs(transport.call_args.kwargs["credentials"], credentials)


if __name__ == "__main__":
    unittest.main()
