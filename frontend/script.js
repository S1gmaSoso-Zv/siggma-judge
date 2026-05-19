const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
    mode: "python", theme: "dracula", lineNumbers: true, indentUnit: 4, matchBrackets: true
});

const runBtn = document.getElementById("runBtn");
const getTaskBtn = document.getElementById("getTaskBtn");
const topicSelect = document.getElementById("topicSelect");
const difficultySelect = document.getElementById("difficultySelect");
const chatBox = document.getElementById("chat");

let currentTaskText = "";
let previousTopic = ""; 

getTaskBtn.addEventListener("click", async () => {
    const topic = topicSelect.value;
    const difficulty = difficultySelect.value;
    
   
    if (previousTopic !== "" && previousTopic !== topic) {
        chatBox.innerHTML = `привет. выбери тему и сложность сверху, нажми "дай задачу", либо просто пиши код.`;
    }
    previousTopic = topic; 

    getTaskBtn.disabled = true;
    getTaskBtn.innerText = "⏳";
    chatBox.innerHTML += `\n\n> генерирую задачу (${difficulty}) на тему: ${topicSelect.options[topicSelect.selectedIndex].text}...`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("http://127.0.0.1:8000/api/generate_task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                topic: topic, 
                difficulty: difficulty
            })
        });
        
        const data = await response.json();
        currentTaskText = data.task;
        
        chatBox.innerHTML += `\n\n🎯 НОВАЯ ЗАДАЧА:\n${currentTaskText}`;
    } catch (error) {
        chatBox.innerHTML += `\n\n❌ ошибка связи с сервером.`;
    } finally {
        getTaskBtn.disabled = false;
        getTaskBtn.innerText = "Дай задачу!";
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});

runBtn.addEventListener("click", async () => {
    const code = editor.getValue();
    const inputData = document.getElementById("stdin-input").value; 
    if (!code.trim()) return;

    runBtn.disabled = true;
    runBtn.innerText = "⏳ проверяю...";
    chatBox.innerHTML += `\n\n> код отправлен...`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("http://127.0.0.1:8000/api/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                code: code,
                task_text: currentTaskText,
                input_data: inputData
            })
        });

        const data = await response.json();

        let reply = `\n\n[вердикт сервера]`;
        if (data.execution.status === "error" || data.execution.status === "timeout") {
            reply += `\n❌ ошибка (${data.execution.time_ms} мс):\n${data.execution.error}`;
        } else {
            reply += `\n✅ успешно (${data.execution.time_ms} мс)\nвывод консоли:\n${data.execution.output || '(пусто)'}`;
        }
        
        reply += `\n\n🤖 ментор:\n${data.ai_feedback}`;
        chatBox.innerHTML += reply;

    } catch (error) {
        chatBox.innerHTML += `\n\n❌ ошибка связи.`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "🚀 отправить на проверку";
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
