async function walletAction(action, amount = 0) {
  try {
    const res = await fetch("/api/wallet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, amount }),
    });

    const data = await res.json();

    if (data.error) {
      document.getElementById("output").innerText = `Error: ${data.error}`;
    } else if (data.message) {
      document.getElementById("output").innerText = data.message;
    } else {
      document.getElementById("output").innerText = "No response message.";
    }
  } catch (err) {
    document.getElementById("output").innerText = "Request failed.";
    console.error(err);
  }
}

function getAmount() {
  const amountInput = document.getElementById("amount").value;
  return parseFloat(amountInput) || 0;
}

function addBalance() {
  const amount = getAmount();
  walletAction("add", amount);
}

function subBalance() {
  const amount = getAmount();
  walletAction("subtract", amount);
}

function checkBalance() {
  walletAction("check");
}

function rewardUser() {
  walletAction("reward");
}

function freezeUser() {
  walletAction("freeze");
}

function unfreezeUser() {
  walletAction("unfreeze");
}

function convertCurrency() {
  walletAction("convert");
}
