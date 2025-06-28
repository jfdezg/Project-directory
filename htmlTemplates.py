css = '''
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    padding: 1rem;
}

.chat-message {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    border-radius: 0.5rem;
    padding: 1rem;
    background-color: #f1f1f1;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chat-message.user {
    background-color: #d1e7dd;
    align-self: flex-end;
}

.chat-message.bot {
    background-color: #ffffff;
    align-self: flex-start;
}

.chat-message .avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.chat-message .message {
    max-width: 85%;
    color: #212529;
    font-size: 1rem;
    line-height: 1.5;
    white-space: pre-wrap;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''
