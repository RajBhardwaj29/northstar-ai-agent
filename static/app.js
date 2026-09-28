let sessionId = createSessionId();

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const typingIndicator = document.getElementById("typingIndicator");
const newConversationButton = document.getElementById("newConversation");

function createSessionId() {
    return "web-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8);
}

function addMessage(role, text) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}-message`;

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = role === "user" ? "You" : "Northstar AI";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    wrapper.appendChild(label);
    wrapper.appendChild(bubble);

    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatConfiguration(value) {
    if (!value) return "—";
    if (value === "2_bhk") return "2 BHK";
    if (value === "3_bhk") return "3 BHK";
    return value;
}

function formatBudget(value) {
    if (!value) return "—";

    const crore = value / 10000000;
    return "₹" + crore.toFixed(crore % 1 === 0 ? 0 : 2) + " Cr";
}

function formatPurpose(value) {
    if (!value || value === "unknown") return "—";
    if (value === "end_use") return "End use";
    if (value === "investment") return "Investment";
    return value;
}

function pretty(value) {
    if (!value) return "Unknown";

    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, char => char.toUpperCase());
}

function updateLeadState(state) {
    document.getElementById("stateLanguage").textContent =
        pretty(state.language);

    document.getElementById("stateConfiguration").textContent =
        formatConfiguration(state.configuration);

    document.getElementById("stateBudget").textContent =
        formatBudget(state.budget);

    document.getElementById("statePurpose").textContent =
        formatPurpose(state.purchase_purpose);

    document.getElementById("stateInterest").textContent =
        pretty(state.interest_level);

    document.getElementById("stateVisit").textContent =
        pretty(state.site_visit_status);

    document.getElementById("stateFollowup").textContent =
        state.follow_up_required
            ? (state.follow_up_time ? "Yes — " + state.follow_up_time : "Yes")
            : "No";

    document.getElementById("stateEscalation").textContent =
        state.human_escalation_required ? "Yes" : "No";

    document.getElementById("stateDnc").textContent =
        state.do_not_contact ? "YES" : "No";
}

async function updateAnalytics() {
    try {
        const response = await fetch(`/analytics/${sessionId}`);

        if (!response.ok) {
            throw new Error("Analytics request failed");
        }

        const analytics = await response.json();

        const score = analytics.qualification.lead_score;

        document.getElementById("leadScore").textContent = score;
        document.getElementById("scoreFill").style.width = score + "%";

        const interest = analytics.qualification.interest_level;

        document.getElementById("analyticsStatus").textContent =
            pretty(interest) +
            " interest lead · " +
            analytics.conversation.message_count +
            " messages";

    } catch (error) {
        console.error("Analytics error:", error);
    }
}

async function sendMessage(message) {
    const cleanMessage = message.trim();

    if (!cleanMessage) {
        return;
    }

    addMessage("user", cleanMessage);

    messageInput.value = "";
    sendButton.disabled = true;
    typingIndicator.classList.remove("hidden");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: cleanMessage
            })
        });

        if (!response.ok) {
            throw new Error("Chat request failed");
        }

        const data = await response.json();

        addMessage("agent", data.response);
        updateLeadState(data.lead_state);

        await updateAnalytics();

    } catch (error) {
        console.error("Chat error:", error);

        addMessage(
            "agent",
            "Something went wrong. Please try again."
        );

    } finally {
        typingIndicator.classList.add("hidden");
        sendButton.disabled = false;
        messageInput.focus();
    }
}

chatForm.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(messageInput.value);
});

document.querySelectorAll(".quick-test").forEach(function (button) {
    button.addEventListener("click", function () {
        messageInput.value = button.dataset.message;
        messageInput.focus();
    });
});

newConversationButton.addEventListener("click", async function () {
    try {
        await fetch(`/session/${sessionId}`, {
            method: "DELETE"
        });
    } catch (error) {
        console.error(error);
    }

    sessionId = createSessionId();

    chatMessages.innerHTML = `
        <div class="message agent-message">
            <div class="message-label">
                Northstar AI
            </div>

            <div class="message-bubble">
                Hi! I can help you with Northstar One in Sector 79, Gurugram.
                What are you looking for?
            </div>
        </div>
    `;

    updateLeadState({
        language: "unknown",
        configuration: null,
        budget: null,
        purchase_purpose: null,
        interest_level: "unknown",
        site_visit_status: "not_requested",
        follow_up_required: false,
        follow_up_time: null,
        human_escalation_required: false,
        do_not_contact: false
    });

    document.getElementById("leadScore").textContent = "0";
    document.getElementById("scoreFill").style.width = "0%";
    document.getElementById("analyticsStatus").textContent =
        "Start a conversation to qualify this lead.";
});