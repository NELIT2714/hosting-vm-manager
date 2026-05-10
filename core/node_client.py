import grpc
from proto import node_agent_pb2, node_agent_pb2_grpc


class NodeClient:

    def __init__(self, address: str, ca_cert: bytes, client_cert: bytes, client_key: bytes):
        credentials = grpc.ssl_channel_credentials(
            root_certificates=ca_cert,
            certificate_chain=client_cert,
            private_key=client_key
        )
        self.channel = grpc.secure_channel(address, credentials)
        self.stub = node_agent_pb2_grpc.NodeAgentStub(self.channel)

    def create_vm(self, vm_name: str, ram_mb: int, vcpus: int, disk_gb: int, base_image: str) -> dict:
        response = self.stub.CreateVM(node_agent_pb2.CreateVMRequest(
            vm_name=vm_name,
            ram_mb=ram_mb,
            vcpus=vcpus,
            disk_gb=disk_gb,
            base_image=base_image
        ))
        return {"vm_name": response.vm_name, "status": response.status, "uuid": response.uuid}

    def delete_vm(self, vm_name: str) -> dict:
        response = self.stub.DeleteVM(node_agent_pb2.VMRequest(vm_name=vm_name))
        return {"vm_name": response.vm_name, "status": response.status}

    def start_vm(self, vm_name: str) -> dict:
        response = self.stub.StartVM(node_agent_pb2.VMRequest(vm_name=vm_name))
        return {"vm_name": response.vm_name, "status": response.status}

    def stop_vm(self, vm_name: str) -> dict:
        response = self.stub.StopVM(node_agent_pb2.VMRequest(vm_name=vm_name))
        return {"vm_name": response.vm_name, "status": response.status}

    def get_vm(self, vm_name: str) -> dict:
        response = self.stub.GetVM(node_agent_pb2.VMRequest(vm_name=vm_name))
        return {"vm_name": response.vm_name, "status": response.status, "uuid": response.uuid}

    def list_vms(self) -> list:
        response = self.stub.ListVMs(node_agent_pb2.Empty())
        return [{"vm_name": vm.vm_name, "status": vm.status, "uuid": vm.uuid} for vm in response.vms]

    def close(self):
        self.channel.close()
