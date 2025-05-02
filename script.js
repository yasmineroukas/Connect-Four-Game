const ROWS = 6;
const COLS = 7;
let boardState = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
let currentPlayer = 1;
let gameActive = true;

const board = document.getElementById("board");
const statusDiv = document.getElementById("status");
const resetButton = document.getElementById("reset-button");

// Initialize the game
function initGame() {
    createBoard();
    setupColumnMarkers();
    setupCellClickHandlers(); // Nouvelle fonction pour gérer les clics sur les cellules
    getGameState();
    
    // Debug
    console.log("Game initialized");
    console.log("Board elements:", document.querySelectorAll('.cell').length);
}

// Create the board cells
function createBoard() {
    board.innerHTML = '';
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const cell = document.createElement("div");
            cell.className = "cell";
            cell.dataset.row = r;
            cell.dataset.col = c;
            board.appendChild(cell);
        }
    }
}

// Set up column click markers - Version améliorée
function setupColumnMarkers() {
    const markers = document.querySelectorAll(".marker");
    markers.forEach(marker => {
        marker.addEventListener("click", function() {
            if (!gameActive) return;
            const col = parseInt(this.dataset.col);
            console.log("Column marker clicked:", col);
            makeMove(col);
        });
        
        // Style visuel pour indiquer les colonnes cliquables
        marker.style.cursor = "pointer";
        marker.style.transition = "all 0.2s";
        marker.addEventListener("mouseenter", () => {
            marker.style.transform = "translateY(5px)";
        });
        marker.addEventListener("mouseleave", () => {
            marker.style.transform = "translateY(0)";
        });
    });
}

// Alternative: Gestion des clics directement sur les cellules
function setupCellClickHandlers() {
    board.addEventListener("click", function(e) {
        if (!gameActive) return;
        
        const cell = e.target.closest(".cell");
        if (!cell) return;
        
        const col = parseInt(cell.dataset.col);
        console.log("Cell clicked in column:", col);
        makeMove(col);
    });
}

// Update the visual board
function updateBoard() {
    const cells = document.querySelectorAll(".cell");
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        // Reset classes
        cell.className = "cell";
        
        // Apply appropriate player class
        if (boardState[row][col] === 1) {
            cell.classList.add("player1");
            cell.innerHTML = "●"; // Ajout d'un symbole visuel
        } else if (boardState[row][col] === 2) {
            cell.classList.add("player2");
            cell.innerHTML = "●"; // Ajout d'un symbole visuel
        }
    });
}

// Make a move in the specified column
function makeMove(col) {
    // Frontend validation
    if (col < 0 || col >= COLS || isNaN(col)) {
        console.error("Invalid column:", col);
        return;
    }
    
    if (boardState[0][col] !== 0) {
        showMessage("Cette colonne est pleine !");
        return;
    }

    // Disable interactions during processing
    setGameActive(false);
    showMessage("En attente...");
    
    // Debug
    console.log("Sending move to server - Column:", col, "Player:", currentPlayer);
    
    // Send move to the server
    fetch("/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ column: col, player: currentPlayer })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Server response:", data);
        
        // Update the board with the new state
        boardState = data.board;
        updateBoard();
        
        // Handle game status
        if (data.status === "win") {
            const winner = data.winner === 1 ? "Vous avez" : "L'IA a";
            showMessage(`🎉 ${winner} gagné !`);
            setGameActive(false);
        } else if (data.status === "draw") {
            showMessage("🤝 Match nul !");
            setGameActive(false);
        } else {
            showMessage("À toi de jouer !");
            setGameActive(true);
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
        showMessage("Erreur de communication avec le serveur");
        setGameActive(true);
    });
}

// Reset the game
function resetGame() {
    console.log("Resetting game...");
    
    fetch("/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        boardState = data.board;
        currentPlayer = data.current_player;
        updateBoard();
        showMessage("Nouvelle partie ! À toi de jouer !");
        setGameActive(true);
    })
    .catch(error => {
        console.error("Reset error:", error);
        showMessage("Erreur lors de la réinitialisation");
    });
}

// Get the current game state from the server
function getGameState() {
    fetch("/state")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            boardState = data.board;
            currentPlayer = data.current_player;
            updateBoard();
            
            if (data.status === "end") {
                showMessage("Partie terminée");
                setGameActive(false);
            } else {
                showMessage(currentPlayer === 1 ? "À toi de jouer !" : "Tour de l'IA...");
                setGameActive(currentPlayer === 1);
            }
        })
        .catch(error => {
            console.error("State fetch error:", error);
            showMessage("Erreur de chargement de l'état du jeu");
        });
}

// Show a message in the status div
function showMessage(message) {
    statusDiv.textContent = message;
    console.log("Status message:", message);
}

// Enable or disable game interactivity
function setGameActive(active) {
    gameActive = active;
    const markers = document.querySelectorAll(".marker");
    
    if (markers) {
        markers.forEach(marker => {
            marker.style.cursor = active ? "pointer" : "not-allowed";
            marker.style.opacity = active ? "1" : "0.5";
        });
    }
    
    // Debug
    console.log("Game active:", active);
}

// Event listeners
resetButton.addEventListener("click", resetGame);

// Initialize the game when the page loads
document.addEventListener("DOMContentLoaded", initGame);