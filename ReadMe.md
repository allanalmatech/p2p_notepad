# 📝 P2P Notepad – A Decentralized Real-Time Collaborative Editor

P2P Notepad is a lightweight, real-time collaborative text editor designed to work **without any centralized server**. It uses **peer-to-peer (P2P)** networking over **TCP sockets**, allowing multiple users on the same LAN or across the internet (with port forwarding) to edit shared documents collaboratively.

---

## 🚀 Features

- ✅ Real-time text synchronization across peers  
- ✅ Peer-to-peer architecture using TCP  
- ✅ LAN-based automatic discovery via UDP broadcast  
- ✅ Manual IP-based connection via `peers.json`  
- ✅ Lamport Clock-based conflict resolution  
- ✅ Fault tolerance and auto-reconnect with exponential backoff  
- ✅ UI shows peer status, connection count, and dynamic updates  
- ✅ File save and undo/redo functionality  
- ✅ Nickname support for peers (via config)  
- ✅ Duplicate IP filtering in UI display  

---

## 🛠 Technology Stack

- **Language**: Python 3.x  
- **GUI**: Tkinter  
- **Networking**: TCP/UDP  
- **Concurrency**: Python’s `threading` module  
- **Data Serialization**: JSON (newline-delimited)  
- **Sync Logic**: Lamport Logical Clock  

---

## 📁 File Structure

```
├── p2p_notepad.py       # Main application
├── shared.py            # Serialization and Lamport clock logic
├── logs.py              # Event logging
├── peers.json           # Config for peer IPs and nicknames
└── shared_note.txt      # (Optional) saved file from notepad
```

---

## 📦 Installation

1. **Clone the repo** or download the `.zip`:
```bash
git clone https://github.com/allanalmatech/p2p-notepad.git
cd p2p-notepad
```

2. **Run the app**:
```bash
python p2p_notepad.py
```

> Requires Python 3.8 or newer.

---

## 🌐 Internet Mode (Optional)

To connect peers over the internet:
- Use public IPs or DDNS in `peers.json`
- Forward TCP port `5001` on each peer's router
- Ensure firewall rules allow the connection
- UDP auto-discovery may not work across WAN

---

## 🧠 peers.json Format

```json
{
  "peers": [
    { "ip": "192.168.0.101", "nickname": "Alice" },
    { "ip": "192.168.0.102", "nickname": "Bob" }
  ]
}
```

---

## 📌 Roadmap & Future Improvements

- [ ] Rich text formatting  
- [ ] Collaborative cursors  
- [ ] End-to-end encryption  
- [ ] WebRTC support  
- [ ] Chat and presence indicators  

---

## 📃 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Credits

**Ainamaani Allan Mwesigye**, 
**Ignatius Tindyebwa**, 
**Nuwahereza Alphat**, 
**Kihembo Daniel**, 
**Ahebwa Faith**, 
**Nyakato Sheillah**, 
2025
