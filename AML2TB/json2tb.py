import logging
import json
from pprint import pprint

# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ThingsBoard REST API URL
url = "http://localhost:8080"

# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"


def main():
    # Creating the REST client object with context manager to get auto token refresh
    with RestClientCE(base_url=url) as rest_client:
        try:
            # Auth with credentials
            rest_client.login(username=username, password=password)

            # Create an Asset Profile
            asset_profile = AssetProfile(
                name="Factory Component", description="General Factory Component"
            )
            asset_profile = rest_client.save_asset_profile(asset_profile)

            # Stores created device profiles
            unique_device_profiles = {}

            # We use these counters to ensure unique naming
            device_counter = {}
            asset_counter = {}

            def create_device_or_asset(obj, rest_client):
                entity = None
                if "ExternalInterface" in obj:
                    external_interface = obj["ExternalInterface"]
                    interface_ref_base_path = external_interface["RefBaseClassPath"]
                    # Value of RefBaseClassPath is like this: "InterfaceClassLib/DCMotor", so we keep only what's after the /
                    interface_device_profile = interface_ref_base_path.split("/")[-1]
                    if interface_device_profile not in unique_device_profiles:
                        device_profile = DeviceProfile(
                            name=interface_device_profile,
                            type="DEFAULT",
                            transport_type="DEFAULT",
                            provision_type="ALLOW_CREATE_NEW_DEVICES",
                            description="Device Profile for "
                            + interface_device_profile,
                            profile_data=DeviceProfileData(
                                configuration={"type": "DEFAULT"},
                                transport_configuration={"type": "DEFAULT"},
                            ),
                        )
                        device_profile = rest_client.save_device_profile(device_profile)
                        # Add the device profile to the unique device profiles
                        unique_device_profiles[
                            interface_device_profile
                        ] = device_profile

                    device_name = obj["Name"]
                    # Increment the count for the current device name, or initialize to 1 if not previously encountered
                    device_counter[device_name] = device_counter.get(device_name, 0) + 1

                    entity = Device(
                        name=f"{device_name}_{device_counter[device_name]}",
                        type="default",
                        device_profile_id=unique_device_profiles[
                            interface_device_profile
                        ].id,
                        additional_info=json.dumps(
                            external_interface.get("Attribute", "")
                        ),
                    )
                    entity = rest_client.save_device(entity)
                    print(
                        f"Device {entity.name} created and assigned to device profile {unique_device_profiles[interface_device_profile].name}"
                    )
                else:
                    asset_name = obj["Name"]
                    # Increment the count for the current asset name, or initialize to 1 if not previously encountered
                    asset_counter[asset_name] = asset_counter.get(asset_name, 0) + 1

                    entity = Asset(
                        name=f"{asset_name}_{asset_counter[asset_name]}",
                        asset_profile_id=asset_profile.id,
                    )
                    entity = rest_client.save_asset(entity)
                    print(
                        f"Asset {entity.name} created and assigned to asset profile {asset_profile.name}"
                    )
                return entity

            def iterate_json(obj, rest_client, parent=None, depth=0):
                # If the object is a list, recursively call iterate_json for each item
                if isinstance(obj, list):
                    for item in obj:
                        iterate_json(item, rest_client, parent, depth)
                else:
                    # Create a device or asset entity based on the information in obj
                    entity = create_device_or_asset(obj, rest_client)

                    # If a parent entity is provided, create a relation between the parent and the current entity
                    if parent is not None:
                        relation = EntityRelation(
                            _from=parent.id, to=entity.id, type="Contains"
                        )
                        rest_client.save_relation(relation)
                        print(f"Relation from {parent.name} to {entity.name} created")

                    # If the object contains an "InternalElement" field, recursively call iterate_json for those elements, treating the current entity as the parent
                    if "InternalElement" in obj:
                        iterate_json(
                            obj["InternalElement"], rest_client, entity, depth + 1
                        )

            with open("factory.json") as json_file:
                data = json.load(json_file)
                iterate_json(data["InstanceHierarchy"], rest_client)

        except ApiException as e:
            logging.exception(e)


if __name__ == "__main__":
    main()
