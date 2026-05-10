import asyncio
import grpc
import os
from grpc import aio
from dotenv import load_dotenv
from proto import vm_manager_pb2, vm_manager_pb2_grpc
from core.node_client import NodeClient
from core.scheduler import Scheduler

load_dotenv()

PORT = int(os.getenv("GRPC_PORT", 50052))
CERTS_CA_PATH = os.getenv("CERTS_CA_PATH")
CERTS_CLIENT_PATH = os.getenv("CERTS_CLIENT_PATH")
CERTS_CLIENT_KEY_PATH = os.getenv("CERTS_CLIENT_KEY_PATH")

CERTS_SERVER_PATH = os.getenv("CERTS_SERVER_PATH")
CERTS_SERVER_KEY_PATH = os.getenv("CERTS_SERVER_KEY_PATH")


def load_certs():
    with open(f"{CERTS_CA_PATH}", "rb") as f:
        ca_cert = f.read()

    with open(f"{CERTS_CLIENT_PATH}", "rb") as f:
        client_cert = f.read()

    with open(f"{CERTS_CLIENT_KEY_PATH}", "rb") as f:
        client_key = f.read()

    return ca_cert, client_cert, client_key


class VMManagerServicer(vm_manager_pb2_grpc.VMManagerServicer):

    def __init__(self):
        self.ca_cert, self.client_cert, self.client_key = load_certs()

    def _build_nodes(self, addresses: list[str]) -> list[NodeClient]:
        return [
            NodeClient(addr, self.ca_cert, self.client_cert, self.client_key)
            for addr in addresses
            if addr.strip()
        ]

    async def CreateVM(self, request, context):
        nodes = self._build_nodes(request.nodes)
        node = Scheduler(nodes).pick_node()
        result = node.create_vm(
            request.vm_name,
            request.ram_mb,
            request.vcpus,
            request.disk_gb,
            request.base_image
        )
        return vm_manager_pb2.VMResponse(
            vm_name=result["vm_name"],
            status=result["status"],
            uuid=result["uuid"]
        )

    async def DeleteVM(self, request, context):
        nodes = self._build_nodes(request.nodes)
        node = Scheduler(nodes).pick_node()
        result = node.delete_vm(request.vm_name)
        return vm_manager_pb2.VMResponse(
            vm_name=result["vm_name"],
            status=result["status"]
        )

    async def StartVM(self, request, context):
        nodes = self._build_nodes(request.nodes)
        node = Scheduler(nodes).pick_node()
        result = node.start_vm(request.vm_name)
        return vm_manager_pb2.VMResponse(
            vm_name=result["vm_name"],
            status=result["status"]
        )

    async def StopVM(self, request, context):
        nodes = self._build_nodes(request.nodes)
        node = Scheduler(nodes).pick_node()
        result = node.stop_vm(request.vm_name)
        return vm_manager_pb2.VMResponse(
            vm_name=result["vm_name"],
            status=result["status"]
        )

    async def GetVM(self, request, context):
        nodes = self._build_nodes(request.nodes)
        node = Scheduler(nodes).pick_node()
        result = node.get_vm(request.vm_name)
        return vm_manager_pb2.VMResponse(
            vm_name=result["vm_name"],
            status=result["status"],
            uuid=result["uuid"]
        )

    async def ListVMs(self, request, context):
        nodes = self._build_nodes(request.nodes)
        node = Scheduler(nodes).pick_node()
        vms = node.list_vms()
        return vm_manager_pb2.ListVMsResponse(
            vms=[
                vm_manager_pb2.VMResponse(
                    vm_name=vm["vm_name"],
                    status=vm["status"],
                    uuid=vm["uuid"]
                )
                for vm in vms
            ]
        )


async def serve():
    ca_cert, client_cert, client_key = load_certs()

    with open(f"{CERTS_SERVER_PATH}", "rb") as f:
        server_cert = f.read()

    with open(f"{CERTS_SERVER_KEY_PATH}", "rb") as f:
        server_key = f.read()

    credentials = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=True
    )

    server = aio.server()
    vm_manager_pb2_grpc.add_VMManagerServicer_to_server(VMManagerServicer(), server)
    server.add_secure_port(f"0.0.0.0:{PORT}", credentials)

    await server.start()

    print(f"VM Manager started on port {PORT} (TLS)")

    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())