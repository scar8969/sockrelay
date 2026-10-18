import asyncio
import socket
import struct

from .accounting import TrafficCounter


class ShadowSocksServer:
    def __init__(self, host: str, port: int, counter: TrafficCounter):
        self.host = host
        self.port = port
        self.counter = counter

    async def start(self):
        server = await asyncio.start_server(self._handle_tcp, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def _handle_tcp(self, reader, writer):
        try:
            # header: [1 byte addr type][addr][2 byte port]
            head = await reader.readexactly(1)
            addr_type = head[0]
            if addr_type == 1:  # IPv4
                raw = await reader.readexactly(4)
                host = socket.inet_ntop(socket.AF_INET, raw)
            elif addr_type == 3:  # domain
                ln = (await reader.readexactly(1))[0]
                host = (await reader.readexactly(ln)).decode()
            elif addr_type == 4:  # IPv6
                raw = await reader.readexactly(16)
                host = socket.inet_ntop(socket.AF_INET6, raw)
            else:
                writer.close()
                return
            port = struct.unpack(">H", await reader.readexactly(2))[0]
            # relay
            r_reader, r_writer = await asyncio.open_connection(host, port)

            async def pump(src, dst, up):
                while True:
                    data = await src.read(65536)
                    if not data:
                        break
                    dst.write(data)
                    await dst.drain()
                    self.counter.add(0, up, 0) if up else self.counter.add(0, 0, len(data))

            await asyncio.gather(pump(reader, r_writer, True), pump(r_reader, writer, False))
        except Exception:
            pass
        finally:
            try:
                writer.close()
            except Exception:
                pass

    async def _handle_udp(self, packet):
        pass
