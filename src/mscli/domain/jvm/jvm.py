
from typing import List
from ..entity.json_data import JSONData
from .version import JVMVersion

class JVMConfiguration(JSONData):
    
    def get_versions(self):
        for version, data in self.json_data["jvm"].items():
            yield JVMVersion(
                name=version,
                providers=data["providers"]
            )

    def get_version(self, version_name: str) -> JVMVersion:
        for version in self.get_versions():
            if version.name == version_name:
                return version
        return None

    def validate(self) -> bool:
        return "jvm" in self.json_data

    @staticmethod
    def create():
        return JVMConfiguration(
            json_data={
                "jvm": {
                    "1.8": {
                        "providers": {
                            "liberica": {
                                "osx": {
                                    "x86": {
                                        "url": "https://download.bell-sw.com/java/8u312+7/bellsoft-jre8u312+7-macos-amd64.zip",
                                        "checksum": "SHA1+e483721c2d249750c88d2591010db52c0b6279e6"
                                    },
                                    "arm": {
                                        "url": "https://download.bell-sw.com/java/8u312+7/bellsoft-jre8u312+7-macos-aarch64.zip",
                                        "checksum": "SHA1+14a1a137f5696c3281b8836925d53c49ea2b5a9c"
                                    }
                                },
                                "linux": {
                                    "x86": {
                                        "url": "https://download.bell-sw.com/java/8u312+7/bellsoft-jre8u312+7-linux-amd64.tar.gz",
                                        "checksum": "SHA1+782fdd5a000bcad073c8b2380c5c4bd90d54ed7f"
                                    },
                                    "arm": {
                                        "url": "https://download.bell-sw.com/java/8u312+7/bellsoft-jre8u312+7-linux-aarch64.tar.gz",
                                        "checksum": "SHA1+d87171f5842557abeedf71eb743854b38fdd90e7"
                                    }
                                },
                                "windows": {
                                    "x86": {
                                        "url": "https://download.bell-sw.com/java/8u312+7/bellsoft-jre8u312+7-windows-amd64.zip",
                                        "checksum": "SHA1+318795c084f5114ef4bcc34b0381538cc81070d5"
                                    }
                                },
                            }
                        }
                    },
                    "1.17": {
                        "providers": {
                            "liberica": {
                                "osx": {
                                    "x86": {
                                        "url": "https://download.bell-sw.com/java/17.0.1+12/bellsoft-jre17.0.1+12-macos-amd64.zip",
                                        "checksum": "a6480fcd5dc906f88502b682ecf38f135c728abf"
                                    },
                                    "arm": {
                                        "url": "https://download.bell-sw.com/java/17.0.1+12/bellsoft-jre17.0.1+12-macos-aarch64.zip",
                                        "checksum": "e50afe673820c24161659b01d40a664fbff002ae"
                                    }
                                },
                                "linux": {
                                    "x86": {
                                        "url": "https://download.bell-sw.com/java/17.0.1+12/bellsoft-jre17.0.1+12-linux-amd64.tar.gz",
                                        "checksum": "2b7c967eb0533bbdd361c228dbd5f1d7e3dd4305"
                                    },
                                    "arm": {
                                        "url": "https://download.bell-sw.com/java/17.0.1+12/bellsoft-jre17.0.1+12-linux-aarch64.tar.gz",
                                        "checksum": "1350a89cbce7457bb787e315201592a95e26f791"
                                    }
                                },
                                "windows": {
                                    "x86": {
                                        "url": "https://download.bell-sw.com/java/17.0.1+12/bellsoft-jre17.0.1+12-windows-amd64.zip",
                                        "checksum": "e7be28c48ee7120c339880efb8b2d7c67ed11452"
                                    }
                                },
                            }
                        }
                    }
                }
            }
        )