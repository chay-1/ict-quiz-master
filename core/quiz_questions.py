import random

# ───────────────────────── Data ─────────────────────────
# We list the quiz topics and the details shown on the topic screen.
TOPICS = [
    {"id": "fundamentals", "name": "Computer Fundamentals", "icon": "🖥️", "level": "Easy",
     "desc": "Learn basic computer concepts and hardware."},
    {"id": "networking", "name": "Networking", "icon": "🌐", "level": "Medium",
     "desc": "Explore networks, protocols and connectivity."},
    {"id": "database", "name": "Database", "icon": "🗄️", "level": "Medium",
     "desc": "Practice database and data management concepts."},
    {"id": "cybersecurity", "name": "Cybersecurity", "icon": "🔒", "level": "Hard",
     "desc": "Test your knowledge of security and online safety."},
]


# We store each question, its choices, correct answer, and explanation together.
def Q(text, opts, ans, why):
    return {"text": text, "options": list(zip("ABCD", opts)), "answer": ans, "why": why}


# We keep the questions grouped by topic. Each topic has ten questions.
BANK = {
    "fundamentals": [
        Q("Which component is commonly referred to as the brain of the computer?",
          ["RAM", "CPU", "Hard Disk", "Monitor"], "B",
          "The CPU (Central Processing Unit) performs all computations and controls the other components."),
        Q("What does RAM stand for?",
          ["Read Access Memory", "Random Access Memory", "Rapid Access Module", "Random Allocated Memory"], "B",
          "RAM is temporary, fast-access memory used by the CPU to store data currently in use."),
        Q("What is the main purpose of an operating system?",
          ["To provide internet connectivity", "To manage hardware and software resources",
           "To create documents and spreadsheets", "To store files on the hard drive"], "B",
          "An operating system manages hardware and software resources and lets applications run."),
        Q("Which of these is an input device?", ["Printer", "Keyboard", "Speaker", "Monitor"], "B",
          "A keyboard sends data into the computer. Printers, speakers and monitors output data."),
        Q("How many bits are there in 1 byte?", ["2", "4", "8", "16"], "C",
          "One byte is made of 8 bits."),
        Q("Which device keeps data even when the computer is switched off?",
          ["RAM", "Cache memory", "SSD", "CPU register"], "C",
          "An SSD (or hard disk) is non-volatile storage. RAM loses its contents when power is off."),
        Q("Which of the following is system software?",
          ["Microsoft Word", "Windows", "Photoshop", "Google Chrome"], "B",
          "Windows is an operating system, which is system software. The others are application software."),
        Q("What does GUI stand for?",
          ["Graphical User Interface", "General User Input", "Graphic Utility Index", "Guided User Interaction"], "A",
          "A GUI lets users interact with a computer through windows, icons and buttons."),
        Q("CPU speed is usually measured in:", ["Gigahertz (GHz)", "Megabytes (MB)", "Pixels", "Decibels"], "A",
          "Clock speed is measured in hertz. Modern CPUs run at several gigahertz."),
        Q("Which file extension is used for a Python program?", [".pt", ".py", ".pyt", ".python"], "B",
          "Python source files end with .py."),
    ],
    "networking": [
        Q("Which protocol is used to assign IP addresses automatically to devices on a network?",
          ["FTP", "HTTP", "DHCP", "SMTP"], "C",
          "DHCP (Dynamic Host Configuration Protocol) assigns IP addresses automatically."),
        Q("What is the function of a router in a network?",
          ["Converts digital signals to analogue", "Directs data packets between different networks",
           "Stores data permanently", "Displays output to the user"], "B",
          "A router directs data packets between networks, choosing the best path."),
        Q("What does HTTPS stand for?",
          ["Hyper Transfer Text Protocol Secure", "HyperText Transfer Protocol Secure",
           "Hybrid Text Transfer Protocol System", "HyperText Transmission Protocol Standard"], "B",
          "HTTPS is the secure version of HTTP, using SSL/TLS encryption."),
        Q("What does LAN stand for?",
          ["Large Area Network", "Local Area Network", "Linked Access Node", "Logical Area Network"], "B",
          "A LAN connects computers in a small area such as a school or lab."),
        Q("Which device connects many computers inside the same network?",
          ["Switch", "Scanner", "Projector", "Webcam"], "A",
          "A switch forwards data between devices on the same network."),
        Q("Which of these is a valid IPv4 address?",
          ["192.168.1.10", "192.168.1.300", "192.168.1", "abc.def.1.1"], "A",
          "IPv4 has four numbers from 0 to 255. 300 is too large."),
        Q("What is the main job of DNS?",
          ["Encrypt web traffic", "Translate domain names into IP addresses",
           "Assign IP addresses", "Block viruses"], "B",
          "DNS works like a phone book: it turns names like google.com into IP addresses."),
        Q("Which topology connects every device to a central switch or hub?",
          ["Bus", "Ring", "Star", "Mesh"], "C",
          "In a star topology each device has its own cable to the centre."),
        Q("Which protocol is used to send email?", ["HTTP", "SMTP", "FTP", "SNMP"], "B",
          "SMTP (Simple Mail Transfer Protocol) sends email between servers."),
        Q("Which cable type sends data using light?",
          ["Coaxial", "Twisted pair", "Fibre optic", "USB"], "C",
          "Fibre optic cables carry data as pulses of light, giving very high speed."),
    ],
    "database": [
        Q("What does SQL stand for in the context of databases?",
          ["Structured Query Language", "Simple Query Logic", "Standard Question Library", "Sequential Query Layer"], "A",
          "SQL is the standard language used to communicate with and manage relational databases."),
        Q("In a relational database, a primary key is used to:",
          ["Link to another database", "Encrypt the table data",
           "Uniquely identify each record in a table", "Sort the records alphabetically"], "C",
          "A primary key uniquely identifies each record; no two rows can share the same value."),
        Q("Which SQL command is used to retrieve data from a table?",
          ["INSERT", "SELECT", "UPDATE", "DELETE"], "B", "SELECT reads data from one or more tables."),
        Q("A row in a database table is also called a:", ["Field", "Record", "Key", "Index"], "B",
          "A row (record) holds all the data about one item. A column is a field."),
        Q("Which SQL command removes rows from a table?", ["DROP", "DELETE", "SELECT", "ALTER"], "B",
          "DELETE removes rows. DROP removes the whole table."),
        Q("A column in a table is called a:", ["Field (attribute)", "Record", "Table", "Query"], "A",
          "Each column stores one kind of data, such as Name or Age. It is called a field."),
        Q("Which of these is a database management system?", ["MySQL", "Notepad", "Paint", "VLC"], "A",
          "MySQL is a relational database management system (DBMS)."),
        Q("A foreign key is used to:",
          ["Encrypt data", "Link two tables together", "Delete a table", "Sort records"], "B",
          "A foreign key in one table refers to the primary key of another table."),
        Q("Which SQL clause filters records?", ["ORDER BY", "GROUP BY", "WHERE", "FROM"], "C",
          "WHERE keeps only the rows that match a condition."),
        Q("Why do organisations back up their databases?",
          ["To make queries faster", "To recover data if it is lost or damaged",
           "To reduce the number of columns", "To rename tables"], "B",
          "Backups let you restore data after failure, mistakes or attacks."),
    ],
    "cybersecurity": [
        Q("Which of the following is an example of a phishing attack?",
          ["Installing a firewall", "Encrypting data on a hard drive",
           "Sending a fake email pretending to be a bank", "Running a virus scan"], "C",
          "Phishing uses deceptive messages, often emails impersonating trusted organisations, to steal information."),
        Q("Which of the following is NOT a type of malware?",
          ["Trojan Horse", "Ransomware", "Firewall", "Spyware"], "C",
          "A firewall filters network traffic. It defends against malware, it is not malware."),
        Q("Which is the strongest password?",
          ["password123", "Pema2005", "T!7m#Qz9$vL2", "qwerty"], "C",
          "Long passwords mixing letters, numbers and symbols, with no personal info, are hardest to guess."),
        Q("What does a firewall do?",
          ["Speeds up the internet", "Filters incoming and outgoing network traffic",
           "Stores backups", "Deletes cookies"], "B",
          "A firewall allows or blocks network traffic based on security rules."),
        Q("What is two-factor authentication (2FA)?",
          ["Using two passwords of the same type", "Proving identity with two different checks",
           "Logging in twice", "Running two antivirus programs"], "B",
          "2FA combines something you know (password) with something you have (a code or phone)."),
        Q("What does ransomware do?",
          ["Locks or encrypts files and demands payment", "Speeds up the computer",
           "Backs up your files", "Blocks pop-up ads"], "A",
          "Ransomware holds your files hostage until a ransom is paid."),
        Q("An email from a stranger has an unexpected attachment. What is the safest action?",
          ["Open it quickly", "Forward it to friends", "Delete it or report it without opening",
           "Reply asking who they are"], "C",
          "Unknown attachments can contain malware. Do not open them."),
        Q("Which habit helps keep your device secure?",
          ["Ignoring software updates", "Installing updates regularly",
           "Turning off antivirus", "Sharing passwords with friends"], "B",
          "Updates fix security holes that attackers could use."),
        Q("What is cyberbullying?",
          ["Using computers for homework", "Using digital platforms to harass or hurt someone",
           "Updating software", "Backing up files"], "B",
          "Cyberbullying is repeated harmful behaviour online. Report it and tell a trusted adult."),
        Q("What should you avoid doing on public Wi-Fi?",
          ["Reading the news", "Entering banking passwords without protection",
           "Listening to music", "Checking the weather"], "B",
          "Public networks can be monitored, so avoid entering sensitive information on them."),
    ],
}


# We match each question with a picture using the same order as the question list.
PIC_ORDER = {
    "fundamentals": ["computer", "ram", "os", "io", "binary", "power", "disc", "pointer", "cpu", "code"],
    "networking": ["laptop", "router", "browser", "building", "hub_q", "ip_q", "globe", "switch",
                   "envelope", "cable"],
    "database": ["table", "key", "clipboard", "table_row", "cabinet", "table_col", "cylinder",
                 "two_tables", "funnel", "drive"],
    "cybersecurity": ["hook", "bug", "padlock", "flame", "shield", "folder", "paperclip", "gear",
                      "phone", "wifi"],
}

# We shuffle the questions and choices, while keeping track of the correct answer.
def prepare(topic_id):
    """Shuffle the questions AND the answer options so every quiz feels new."""
    items = list(zip(BANK[topic_id], PIC_ORDER[topic_id]))
    random.shuffle(items)
    out = []
    for q, pic in items:
        right = dict(q["options"])[q["answer"]]
        texts = [t for _, t in q["options"]]
        random.shuffle(texts)
        out.append({"text": q["text"], "options": list(zip("ABCD", texts)),
                    "answer": "ABCD"[texts.index(right)], "why": q["why"], "pic": pic})
    return out
