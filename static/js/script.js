document.addEventListener('DOMContentLoaded', () => {
    // Sample data
    const contacts = [
        { id: 1, name: 'User 1' },
        { id: 2, name: 'User 2' },
        { id: 3, name: 'User 3' }
    ];

    const messagesData = {
        1: [
            { text: 'Hello User 1!', user: 'user2' },
            { text: 'Hi there!', user: 'user1' }
        ],
        2: [
            { text: 'Hello User 2!', user: 'user1' }
        ]
    };

    const contactList = document.getElementById('contact-list');
    const messagesContainer = document.getElementById('messages');
    const contactName = document.getElementById('contact-name');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    let selectedContactId = null;

    // Populate contact list
    contacts.forEach(contact => {
        const li = document.createElement('li');
        li.textContent = contact.name;
        li.dataset.id = contact.id;
        li.addEventListener('click', () => showMessages(contact.id));
        contactList.appendChild(li);
    });

    // Show messages for selected contact
    function showMessages(contactId) {
        selectedContactId = contactId;
        contactName.textContent = contacts.find(c => c.id === contactId).name;
        messagesContainer.innerHTML = '';
        if (messagesData[contactId]) {
            messagesData[contactId].forEach(message => {
                const div = document.createElement('div');
                div.textContent = message.text;
                div.className = `message ${message.user}`;
                messagesContainer.appendChild(div);
            });
        }
    }

    // Handle form submission
    messageForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (selectedContactId) {
            const messageText = messageInput.value.trim();
            if (messageText) {
                const div = document.createElement('div');
                div.textContent = messageText;
                div.className = 'message user1';
                messagesContainer.appendChild(div);
                messageInput.value = '';

                // Add to messagesData (for demo purposes)
                if (!messagesData[selectedContactId]) {
                    messagesData[selectedContactId] = [];
                }
                messagesData[selectedContactId].push({ text: messageText, user: 'user1' });
            }
        }
    });
});

