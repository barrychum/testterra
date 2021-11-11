import pandas as pd
from pandas import ExcelWriter, ExcelFile

#   credentials = file(var.credentials_file)

df0 = pd.read_excel('input.xlsx', sheet_name='provider')
out = """
terraform {{
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "3.5.0"
    }}
  }}
}}

provider "google" {{
  project = "{project}"
  region  = "{region}"
}} """.format(region=df0.region[0],
project=df0.project[0])

print(out)

df1 = pd.read_excel('input.xlsx', sheet_name='firewall')
out = """
resource "google_compute_firewall" "default" {{
  name    = "{name}"
  network = "{network}"
  source_tags = {tags}
""".format(name=df1.name[0],
network=df1.network[0],
tags=df1.tags[0])

print(out)

for i in df1.index:
    a = str(df1.allow_ports[i])

    if (pd.notna(df1.allow_ports[i])):
        out1 = """
  allow{{
    protocol = "{allow_protocol}"
    ports    = {allow_ports}
  }}
        """.format(allow_protocol=df1.allow_protocol[i],
        allow_ports=df1.allow_ports[i])
    else:
        out1 = """
  allow{{
    protocol = "{allow_protocol}"
  }}
        """.format(allow_protocol=df1.allow_protocol[i])
    print(out1)

print("}")


totalcnt = 0
df3 = pd.read_excel('input.xlsx', sheet_name='instance')
for i in df3.index:
  totalcnt=totalcnt + df3.node_count[i]

staticblock = """
resource "google_compute_address" "static" {{
  count = "6"
  name = "ipv4-address-${{count.index}}"
}}
"""
print(staticblock)

# use the following tags for http / https firewall rules
# tags = ["http-server","https-server"]

df = pd.read_excel('input.xlsx', sheet_name='instance')
for i in df.index:
    out2 = """
resource "google_compute_instance" "{name_prefix}" {{
count        = "{node_count}"
name         = "test-node-${{count.index}}"
machine_type = "{machine_type}"
zone         = "{zone}"
tags         = {tags}

boot_disk {{
    initialize_params {{
    image = "{image}"
    }}
}}

network_interface {{
    network = "{network}"
    access_config {{
    // Ephemeral IP
    // use the following to assign External IP created in compute_address
      nat_ip = "${element(google_compute_address.static.*.address, count.index)}"
    }}
}}
}}
    """.format(name_prefix=df.name_prefix[i],
    node_count=df.node_count[i],
    machine_type=df.machine_type[i],
    zone=df.zone[i],
    tags=df.tags[i],
    image=df.image[i],
    network=df.network[i])

    print(out2)
