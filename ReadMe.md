# 📝 P2P Notepad – A Decentralized Real-Time Collaborative Editor

P2P Notepad is a real-time collaborative text editor built on top of **distributed systems principles**. It works **without any centralized server**, using **peer-to-peer (P2P)** networking over **TCP sockets**, allowing multiple users on the same LAN or across the internet to collaborate securely and efficiently.

---

## 🚀 Features

- ✅ Real-time text synchronization using distributed messaging
- ✅ Peer-to-peer architecture via TCP sockets (direct communication)
- ✅ LAN-based automatic discovery via UDP broadcast
- ✅ Manual peer configuration through `peers.json`
- ✅ Lamport Logical Clocks for conflict resolution
- ✅ Fault tolerance with exponential backoff for reconnections
- ✅ Temporary backup files for session recovery
- ✅ Nicknaming support for peers for easy identification
- ✅ Undo/Redo functionality integrated into editing
- ✅ Duplicate IP prevention in peer listing

---

## 🛠️ Technologies & Distributed Concepts

| Concept | Implementation |
|:---|:---|
| **Peer-to-Peer (P2P)** | Every user acts as both a client and server |
| **Synchronization** | Achieved using TCP message passing and Lamport clocks |
| **Fault Tolerance** | Auto-retry connections, temporary backups, crash recovery |
| **Logical Clocks** | Lamport Clock timestamps every edit to maintain order |
| **Caching (Temporary Backups)** | Locally saves current text to a temp file, recoverable after crashes |
| **Replication** | On every edit, text is replicated to all connected peers |
| **Concurrency** | Threads handle socket communication separately from UI updates |
| **Naming** | Nicknames are mapped to IPs from `peers.json` |
| **Failure Detection** | Dead peers detected when TCP send/recv fails |
| **RPC-like Backup Fetching** | Peers request text backups from others using a mini protocol |
| **UDP Broadcast Discovery** | Automatic peer discovery within LAN using UDP |

---

## 👜 File Structure

```
.
├── p2p_notepad.py       # Main application logic
├── shared.py            # Serialization, deserialization, Lamport clock management
├── logs.py              # Logs major events for fault analysis
├── peers.json           # Static peer IP and nickname configuration
├── temp_backup.txt      # Auto-generated temporary backup per session
├── shared_note.txt      # Saved user notes manually
```

---

## 📆 Installation and Running

```bash
git clone https://github.com/allanalmatech/p2p-notepad.git
cd p2p-notepad
python p2p_notepad.py
```
> Requires Python 3.8 or newer.

---

## 🌐 How Internet Collaboration Works

- Forward TCP port `5001` on each peer's router
- Peers manually configured in `peers.json`
- UDP auto-discovery works only within the same LAN; WAN needs manual connection

---

## 💡 peers.json Example

```json
{
  "peers": [
    { "ip": "192.168.0.101", "nickname": "Alice" },
    { "ip": "192.168.0.102", "nickname": "Bob" }
  ]
}
```

---

## 🔗 Fault Tolerance and Recovery

- **Exponential Backoff:** Attempts reconnection by doubling waiting time after each failure.
- **Backup File:** Saves current state locally in `temp_backup.txt`.
- **Session Recovery:** User can trigger "Recover Backup" if peers or system crash.
- **Parallel Backup Fetching:** Requests from all available peers to find the most recent text.

---

## 🛠️ Future Improvements

- [ ] Rich text formatting and font support
- [ ] Collaborative cursors (like Google Docs)
- [ ] WebRTC for browser-based participation
- [ ] End-to-End encryption for secure editing
- [ ] Peer chat system with presence indicators

---

## 📚 Authors and Acknowledgements

- **Ainamaani Allan Mwesigye**
- **Ignatius Tindyebwa**
- **Nuwahereza Alphat**
- **Kihembo Daniel**
- **Ahebwa Faith**
- **Nyakato Sheillah**

_2025 Distributed systems project._

---

## 📅 License

**MIT License** — Free to use, modify, and distribute without restriction.

---

