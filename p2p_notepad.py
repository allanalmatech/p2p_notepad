import socket
import threading
import time
import json
from tkinter import Tk, Text, END, Label, Menu, Toplevel, Listbox
from shared import LamportClock, serialize, deserialize_stream
from logs import log_event


def load_peer_config(path="peers.json"):
    try:
        with open(path, "r") as f:
            data = json.load(f).get("peers", [])
            return {entry["ip"]: entry.get("nickname", entry["ip"]) for entry in data}
    except Exception as e:
        print(f"[!] Could not load config file: {e}")
        return {}


def save_text_to_file(text, filename="shared_note.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"[!] Save error: {e}")
        return False


class P2PNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Notepad")
        self.text = Text(root, undo=True)
        self.text.pack(fill="both", expand=True)
        self.clock = LamportClock()
        self.peers = set()
        self.peer_lock = threading.Lock()
        self.running = True

        self.nicknames = load_peer_config()
        self.peer_status_label = Label(root, text="Peers: 0", fg="green")
        self.peer_status_label.pack()

        self.setup_menu()
        self.setup_periodic_updates()

        self.udp_port = 5000
        self.tcp_port = 5001
        self.setup_tcp()
        self.setup_udp()

        for ip in self.nicknames.keys():
            threading.Thread(target=self.backoff_connect, args=(ip,), daemon=True).start()
            log_event(f"Manually attempting to connect to {ip}")

        self.text.bind("<KeyRelease>", self.on_edit)

    def setup_menu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_current_note)

        peer_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Peers", menu=peer_menu)
        peer_menu.add_command(label="Show Peers", command=self.show_peers)

        edit_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.text.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text.edit_redo)

    def show_peers(self):
        window = Toplevel(self.root)
        window.title("Connected Peers")
        listbox = Listbox(window, width=50)
        listbox.pack(padx=10, pady=10)
        with self.peer_lock:
            seen_ips = set()
            for peer in self.peers:
                try:
                    ip = peer.getpeername()[0]
                    if ip in seen_ips:
                        continue
                    seen_ips.add(ip)
                    nickname = self.nicknames.get(ip, ip)
                    listbox.insert(END, f"{ip} - {nickname}")
                except:
                    continue

    def setup_periodic_updates(self):
        self.update_peer_display()
        self.root.after(1000, self.setup_periodic_updates)

    def update_peer_display(self):
        with self.peer_lock:
            peer_ips = {peer.getpeername()[0] for peer in self.peers}
            peer_count = len(peer_ips)
        self.peer_status_label.config(text=f"Peers: {peer_count}")
        self._set_status_color(peer_count)

    def status_message(self, message):
        with self.peer_lock:
            peer_ips = {peer.getpeername()[0] for peer in self.peers}
            count = len(peer_ips)
        status_text = f"{count} peer{'s' if count != 1 else ''} online | {message}"
        self.peer_status_label.config(text=status_text)
        self._set_status_color(count)

    def _set_status_color(self, count):
        if count == 0:
            self.peer_status_label.config(fg="red")
        elif count < 3:
            self.peer_status_label.config(fg="orange")
        else:
            self.peer_status_label.config(fg="green")

    def setup_udp(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind(("0.0.0.0", self.udp_port))
        threading.Thread(target=self.broadcast_presence, daemon=True).start()
        threading.Thread(target=self.discover_peers, daemon=True).start()

    def broadcast_presence(self):
        while self.running:
            msg = serialize({"tcp_port": self.tcp_port})
            self.udp_sock.sendto(msg, ("255.255.255.255", self.udp_port))
            time.sleep(3)

    def discover_peers(self):
        while self.running:
            try:
                data, addr = self.udp_sock.recvfrom(1024)
                msg = json.loads(data.decode())
                peer = (addr[0], msg["tcp_port"])
                with self.peer_lock:
                    if peer not in self.peers and peer[1] != self.tcp_port:
                        threading.Thread(target=self.backoff_connect, args=(peer[0],), daemon=True).start()
                        log_event(f"Discovered peer: {peer[0]}:{peer[1]}")
            except:
                continue

    def setup_tcp(self):
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.bind(("0.0.0.0", self.tcp_port))
        self.tcp_sock.listen()
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def backoff_connect(self, ip):
        delay = 1
        while self.running:
            try:
                self.connect_to_peer(ip, self.tcp_port)
                return
            except Exception as e:
                log_event(f"Backoff: failed to connect to {ip} - retrying in {delay}s")
                time.sleep(delay)
                delay = min(delay * 2, 60)

    def add_peer(self, conn):
        with self.peer_lock:
            self.peers.add(conn)
        ip = conn.getpeername()[0]
        name = self.nicknames.get(ip, ip)
        self.status_message(f"{ip} ({name}) joined")

    def remove_peer(self, conn):
        try:
            ip = conn.getpeername()[0]
        except:
            ip = "unknown"
        with self.peer_lock:
            if conn in self.peers:
                self.peers.remove(conn)
        name = self.nicknames.get(ip, ip)
        self.status_message(f"{ip} ({name}) left")
        try:
            conn.close()
        except:
            pass
        if ip in self.nicknames:
            threading.Thread(target=self.backoff_connect, args=(ip,), daemon=True).start()

    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.tcp_sock.accept()
                log_event(f"Incoming connection from {addr[0]}:{addr[1]}")
                self.add_peer(conn)
                threading.Thread(target=self.handle_peer, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[!] Connection accept error: {e}")
                break

    def connect_to_peer(self, peer_ip, peer_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer_ip, peer_port))
        threading.Thread(target=self.handle_peer, args=(sock,), daemon=True).start()
        with self.peer_lock:
            self.peers.add(sock)

    def handle_peer(self, conn):
        peer_ip = conn.getpeername()[0]
        self.add_peer(conn)

        def delayed_initial_sync():
            time.sleep(1)
            current_text = self.text.get("1.0", END).strip()
            if len(current_text) > 5:
                try:
                    lamport = self.clock.increment()
                    conn.send(serialize({"text": current_text, "lamport": lamport}))
                    log_event(f"Sent initial text to {peer_ip}")
                except Exception as e:
                    log_event(f"Failed to send initial text: {e}")

        threading.Thread(target=delayed_initial_sync, daemon=True).start()

        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                messages = deserialize_stream(data)
                for msg in messages:
                    if "text" in msg and "lamport" in msg:
                        self.root.after(0, self.apply_edit, msg["text"], msg["lamport"])
            except Exception as e:
                log_event(f"[!] Peer error: {str(e)}")
                break
        self.remove_peer(conn)
        log_event(f"Disconnected from {peer_ip}")

    def on_edit(self, event=None):
        text = self.text.get("1.0", END).strip()
        lamport = self.clock.increment()
        dead_peers = []
        with self.peer_lock:
            for peer in list(self.peers):
                try:
                    peer.send(serialize({"text": text, "lamport": lamport}))
                except:
                    dead_peers.append(peer)
            for peer in dead_peers:
                try:
                    peer.close()
                except:
                    pass
                self.peers.discard(peer)

    def apply_edit(self, text, received_clock):
        self.clock.update(received_clock)
        self.text.delete("1.0", END)
        self.text.insert(END, text)
        self.text.see(END)

    def save_current_note(self):
        content = self.text.get("1.0", END).strip()
        if save_text_to_file(content):
            self.status_message("Note saved to shared_note.txt")
        else:
            self.status_message("Failed to save note.")

    def on_close(self):
        self.running = False
        try:
            self.tcp_sock.close()
            self.udp_sock.close()
        except:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    app = P2PNotepad(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
