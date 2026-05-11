document.addEventListener('DOMContentLoaded', () => {
    // 1. Inject the toolbar HTML if it doesn't exist
    if (!document.getElementById('global-context-toolbar')) {
        const toolbarHTML = `
        <div class="fixed hidden z-[9999] flex items-center gap-4 bg-white px-6 py-3 rounded-full shadow-lg border border-gray-200 animate-in fade-in zoom-in duration-200" id="global-context-toolbar" style="box-shadow: 0 4px 20px -2px rgba(45,49,66,0.15);">
            <button id="globalReadAloudBtn" class="flex items-center gap-2 group hover:opacity-80 transition-opacity">
                <span class="material-symbols-outlined text-[#B5D99C]" style="font-variation-settings: 'FILL' 1;">volume_up</span>
                <span class="font-bold text-sm text-[#2D3142] whitespace-nowrap">Read Aloud</span>
            </button>
            <div class="w-px h-4 bg-gray-200"></div>
            <button id="globalDictBtn" class="flex items-center gap-2 group hover:opacity-80 transition-opacity">
                <span class="material-symbols-outlined text-[#B5D99C]" style="font-variation-settings: 'FILL' 1;">book_2</span>
                <span class="font-bold text-sm text-[#2D3142] whitespace-nowrap">Instant Dictionary</span>
            </button>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', toolbarHTML);
    }

    const toolbar = document.getElementById('global-context-toolbar');
    const readAloudBtn = document.getElementById('globalReadAloudBtn');
    const dictBtn = document.getElementById('globalDictBtn');

    let cachedWord = "";
    let cachedContext = "";

    // 2. Handle Text Selection
    document.addEventListener('mouseup', function(e) {
        // Don't hide if clicking inside the toolbar itself
        if (toolbar.contains(e.target)) return;

        const selection = window.getSelection();
        const text = selection.toString().trim();
        
        if (text.length > 0) {
            cachedWord = text;
            
            // Try to get a whole sentence context around the selection
            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            if (container.nodeType === Node.TEXT_NODE) {
                cachedContext = container.textContent.trim();
            } else {
                cachedContext = container.innerText || container.textContent || text;
            }

            const rect = range.getBoundingClientRect();
            
            // Position the toolbar above the selection (using fixed coordinates)
            toolbar.style.left = (rect.left + rect.width / 2) + 'px';
            toolbar.style.top = (rect.top - 60) + 'px';
            toolbar.style.transform = 'translateX(-50%)';
            
            toolbar.classList.remove('hidden');
        } else {
            toolbar.classList.add('hidden');
            cachedWord = "";
            cachedContext = "";
        }
    });

    // Prevent toolbar from closing when clicking inside it
    toolbar.addEventListener('mousedown', function(e) {
        e.stopPropagation();
    });

    // 3. Handle Dictionary Click
    dictBtn.addEventListener('click', () => {
        if (cachedWord) {
            sessionStorage.setItem('glossaryWord', cachedWord);
            sessionStorage.setItem('glossaryContext', cachedContext);
            window.location.href = 'glossary.html';
        }
    });

    // 4. Handle Read Aloud Click
    readAloudBtn.addEventListener('click', () => {
        if (cachedWord) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(cachedWord);
            
            // Dyslexia friendly settings: slightly slower rate
            utterance.rate = 0.85; 
            utterance.pitch = 1.0;

            // Try to find a clear English voice
            const voices = window.speechSynthesis.getVoices();
            const preferredVoices = voices.filter(v => 
                v.lang.startsWith('en') && (
                    v.name.includes('Google') || 
                    v.name.includes('Samantha') || 
                    v.name.includes('Premium') ||
                    v.name.includes('Natural')
                )
            );
            
            if (preferredVoices.length > 0) {
                utterance.voice = preferredVoices[0];
            }

            window.speechSynthesis.speak(utterance);
        }
    });

    // Ensure voices are loaded (Chrome sometimes needs this nudge)
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }


});
