import re
import subprocess

from types import SimpleNamespace

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction


icon = 'images/icon.png'


class IPsExtension(Extension):

    def __init__(self):
        super(IPsExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def get_interfaces(self):

        results = []

        cmd = """ifconfig | awk '/^[a-z]+/ {gsub(":", "");print $1}'"""

        interfaces = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = interfaces.communicate()

        if stderr:
            return results

        for i in stdout.decode().split("\n"):

            if not i:
                continue

            cmd = """ifconfig %s | awk '/inet / {print $2}' """ % (i)

            interface = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = interface.communicate()

            results.append(SimpleNamespace(
                **{'iface': i, "ip": stdout.decode().strip("\n")}))

        return results


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        query = event.get_argument()

        interfaces = extension.get_interfaces()

        print(interfaces)

        results = []

        if not query:
            for i in interfaces:
                results.append(ExtensionResultItem(
                    name=i.ip,
                    description=i.iface,
                    icon=icon,
                    on_enter=CopyToClipboardAction(text=i.ip)
                ))

        else:

            query_re = query.replace(" ", ".+")

            for i in interfaces:
                print(query_re, i)
                if re.search(r"%s" % query_re, i.iface, re.I) or re.search(r"%s" % query_re, i.ip, re.I):
                    results.append(
                        ExtensionResultItem(
                            name=i.ip,
                            description=i.iface,
                            icon=icon,
                            on_enter=CopyToClipboardAction(text=i.ip)
                        )
                    )

        return RenderResultListAction(results)


if __name__ == '__main__':
    IPsExtension().run()
