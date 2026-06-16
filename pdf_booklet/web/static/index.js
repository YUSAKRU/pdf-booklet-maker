document.addEventListener('DOMContentLoaded', () => {
    // Translations Dictionary
    const translations = {
        en: {
            tagline: "Local-First, High-Performance PDF Imposition Engine",
            privacy_badge: "100% Offline & Private (Your files never leave your machine)",
            section_config: "1. Upload & Configure",
            drop_title: "Drag & drop your PDF here",
            drop_subtitle: "or click to browse from files",
            drop_limit: "Supports standard Portrait A4 PDFs",
            label_gutter: "Gutter Margin (Fold Space)",
            desc_gutter: "The space left between the pages at the center fold spine.",
            label_creep: "Creep Compensation",
            desc_creep: "Shifts inner pages inward to compensate for paper folding thickness.",
            btn_generate: "Generate Booklet Sheets",
            section_results: "2. Imposition Output",
            placeholder_title: "Waiting for Booklet Generation",
            placeholder_text: "Upload a PDF and customize folding options to preview the output sheets.",
            success_title: "Booklet Generated Successfully!",
            meta_orig: "Original Pages",
            meta_padded: "Padded Blank Pages",
            meta_sheets: "Total Sheets (A4 Landscape)",
            dl_front_title: "Download Front PDF",
            dl_front_desc: "For odd page printing",
            dl_back_title: "Download Back PDF",
            dl_back_desc: "For even page printing",
            dl_zip_title: "Download All (ZIP)",
            dl_zip_desc: "Contains both Front & Back",
            
            // PDF Preview labels
            preview_title: "PDF Live Preview",
            preview_front_tab: "Front (Odd Sheets)",
            preview_back_tab: "Back (Even Sheets)",
            
            // Log messages
            log_upload: "Starting PDF uploading process...",
            log_imposition: "Uploading document parameters and running core imposition engine...",
            log_success: "Booklet generated successfully in engine.",
            log_error: "Imposition engine aborted execution due to anomalies.",
            log_network_error: "Unexpected network error or server disconnect.",
            log_lang_switch: "Language switched to English.",
            
            err_format_title: "Invalid File Format",
            err_format_desc: "Please upload standard PDF files only.",
            err_network_title: "Server Connection Error",
            err_network_desc: "Could not connect to the local server. Make sure the booklet engine is running."
        },
        tr: {
            tagline: "Yerel ve Yüksek Performanslı Kitapçık Dizgileme Motoru",
            privacy_badge: "%100 Çevrimdışı ve Güvenli (Dosyalarınız asla bilgisayarınızdan çıkmaz)",
            section_config: "1. Yükle ve Yapılandır",
            drop_title: "PDF dosyanızı buraya sürükleyin",
            drop_subtitle: "veya dosyalarınızdan seçmek için tıklayın",
            drop_limit: "Standart Dikey A4 PDF'leri destekler",
            label_gutter: "Orta Katlama Boşluğu (Gutter)",
            desc_gutter: "Sayfaların katlanma çizgisinde (ortada) bırakılacak boşluk miktarı.",
            label_creep: "Kağıt Taşma Payı (Creep)",
            desc_creep: "Sayfa kalınlığı nedeniyle iç sayfaların dışarı taşmasını engellemek için içe kaydırma.",
            btn_generate: "Kitapçık Sayfalarını Üret",
            section_results: "2. Dizgileme Çıktısı",
            placeholder_title: "Kitapçık Üretimi Bekleniyor",
            placeholder_text: "Kitapçık şablonlarını görmek için bir PDF yükleyin ve katlama seçeneklerini ayarlayın.",
            success_title: "Kitapçık Başarıyla Üretildi!",
            meta_orig: "Orijinal Sayfa Sayısı",
            meta_padded: "Eklenen Boş Sayfalar",
            meta_sheets: "Toplam Yaprak Sayısı (Yatay A4)",
            dl_front_title: "Ön Yüz PDF'ini İndir",
            dl_front_desc: "Tek numaralı sayfalar için",
            dl_back_title: "Arka Yüz PDF'ini İndir",
            dl_back_desc: "Çift numaralı sayfalar için",
            dl_zip_title: "Tümünü İndir (ZIP)",
            dl_zip_desc: "Ön ve Arka yüz PDF'lerini içerir",
            
            // PDF Preview labels
            preview_title: "PDF Canlı Önizleme",
            preview_front_tab: "Ön Yüz (Tek Sayfalar)",
            preview_back_tab: "Arka Yüz (Çift Sayfalar)",
            
            // Log messages
            log_upload: "PDF yükleme işlemi başlatılıyor...",
            log_imposition: "Belge parametreleri gönderiliyor ve dizgileme motoru çalıştırılıyor...",
            log_success: "Kitapçık dizgileme motorunda başarıyla oluşturuldu.",
            log_error: "Dizgileme motoru anomaliler nedeniyle durduruldu.",
            log_network_error: "Beklenmeyen ağ hatası veya sunucu bağlantısı kesildi.",
            log_lang_switch: "Dil Türkçe olarak değiştirildi.",
            
            err_format_title: "Geçersiz Dosya Formatı",
            err_format_desc: "Lütfen sadece standart PDF formatındaki dosyaları yükleyin.",
            err_network_title: "Sunucu Bağlantı Hatası",
            err_network_desc: "Yerel sunucuya bağlanırken bir hata oluştu. Motorun çalıştığından emin olun."
        }
    };

    // Multi-Language State
    let currentLang = localStorage.getItem('pdf_booklet_lang') || 'en';

    function setLanguage(lang) {
        currentLang = lang;
        localStorage.setItem('pdf_booklet_lang', lang);
        
        // Update elements
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                el.textContent = translations[lang][key];
            }
        });

        // Update selector state
        document.querySelectorAll('.lang-btn').forEach(btn => {
            if (btn.getAttribute('data-lang') === lang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Initialize UI language
    setLanguage(currentLang);

    // Bind selector click events
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const lang = e.target.getAttribute('data-lang');
            setLanguage(lang);
            appendLog("INFO", translations[currentLang].log_lang_switch);
        });
    });

    // Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileDetails = document.getElementById('fileDetails');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    
    const gutterInput = document.getElementById('gutterInput');
    const gutterValue = document.getElementById('gutterValue');
    const creepInput = document.getElementById('creepInput');
    const creepValue = document.getElementById('creepValue');
    
    const bookletForm = document.getElementById('bookletForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnSpinner = document.getElementById('btnSpinner');
    
    const placeholderState = document.getElementById('placeholderState');
    const successActions = document.getElementById('successActions');
    const errorState = document.getElementById('errorState');
    
    const resOriginalPages = document.getElementById('resOriginalPages');
    const resPaddingApplied = document.getElementById('resPaddingApplied');
    const paddingRow = document.getElementById('paddingRow');
    const resSheetsCount = document.getElementById('resSheetsCount');

    // PDF Preview Elements
    const previewCardContainer = document.getElementById('previewCardContainer');
    const pdfPreviewIframe = document.getElementById('pdfPreviewIframe');
    const previewFrontTab = document.getElementById('previewFrontTab');
    const previewBackTab = document.getElementById('previewBackTab');
    
    const downloadFront = document.getElementById('downloadFront');
    const downloadBack = document.getElementById('downloadBack');
    const downloadZip = document.getElementById('downloadZip');

    let selectedFile = null;
    let frontPdfUrl = '';
    let backPdfUrl = '';

    // Slider value changes
    gutterInput.addEventListener('input', (e) => {
        gutterValue.textContent = e.target.value;
    });

    creepInput.addEventListener('input', (e) => {
        creepValue.textContent = parseFloat(e.target.value).toFixed(1);
    });

    // Drag and Drop handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showErrorState(translations[currentLang].err_format_title, translations[currentLang].err_format_desc);
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        
        dropZone.querySelector('.drop-content').classList.add('hidden');
        fileDetails.classList.remove('hidden');
        
        submitBtn.disabled = false;
        submitBtn.classList.remove('disabled');

        resetOutputStates();
    }

    // Remove file handler
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileSelection();
    });

    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        
        dropZone.querySelector('.drop-content').classList.remove('hidden');
        fileDetails.classList.add('hidden');
        
        submitBtn.disabled = true;
        submitBtn.classList.add('disabled');
        
        resetOutputStates();
        placeholderState.classList.remove('hidden');
    }

    function resetOutputStates() {
        placeholderState.classList.add('hidden');
        successActions.classList.add('hidden');
        previewCardContainer.classList.add('hidden');
        errorState.classList.add('hidden');
        
        // Reset preview iframe
        pdfPreviewIframe.src = 'about:blank';
        previewFrontTab.classList.add('active');
        previewBackTab.classList.remove('active');
        frontPdfUrl = '';
        backPdfUrl = '';
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Helper to append logs (Prints to developer console F12)
    function appendLog(level, message, details = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            level: level,
            message: message,
            logger: "pdf-booklet-maker-web",
            details: details
        };
        console.log(`[${logEntry.level}] ${logEntry.message}`, logEntry.details);
    }

    // Bind PDF Preview Tabs
    previewFrontTab.addEventListener('click', () => {
        if (!frontPdfUrl) return;
        pdfPreviewIframe.src = frontPdfUrl + "?inline=true";
        previewFrontTab.classList.add('active');
        previewBackTab.classList.remove('active');
    });

    previewBackTab.addEventListener('click', () => {
        if (!backPdfUrl) return;
        pdfPreviewIframe.src = backPdfUrl + "?inline=true";
        previewBackTab.classList.add('active');
        previewFrontTab.classList.remove('active');
    });

    // Form Submission
    bookletForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        submitBtn.disabled = true;
        btnSpinner.classList.remove('hidden');
        resetOutputStates();
        
        appendLog("INFO", translations[currentLang].log_upload, {
            file_name: selectedFile.name,
            file_size_bytes: selectedFile.size
        });

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('gutter', gutterInput.value);
        formData.append('creep', creepInput.value);

        try {
            appendLog("INFO", translations[currentLang].log_imposition, {
                gutter: parseFloat(gutterInput.value),
                creep: parseFloat(creepInput.value)
            });

            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                appendLog("INFO", translations[currentLang].log_success, {
                    original_pages: result.original_pages,
                    padded_pages: result.padded_pages,
                    sheets_count: result.sheets_count,
                    padding_applied: result.padding_applied
                });

                resOriginalPages.textContent = result.original_pages;
                resSheetsCount.textContent = result.sheets_count;
                
                if (result.padding_applied > 0) {
                    const paddingText = currentLang === 'tr' 
                        ? `+${result.padding_applied} boş sayfa enjekte edildi` 
                        : `+${result.padding_applied} blank pages added`;
                    resPaddingApplied.textContent = paddingText;
                    paddingRow.classList.remove('hidden');
                } else {
                    paddingRow.classList.add('hidden');
                }

                // Cache URLs
                frontPdfUrl = result.download_urls.front;
                backPdfUrl = result.download_urls.back;

                // Bind downloads
                downloadFront.setAttribute('href', frontPdfUrl);
                downloadBack.setAttribute('href', backPdfUrl);
                downloadZip.setAttribute('href', result.download_urls.zip);

                // Set initial PDF preview source (Front page, inline)
                pdfPreviewIframe.src = frontPdfUrl + "?inline=true";

                // Update UI layout
                placeholderState.classList.add('hidden');
                successActions.classList.remove('hidden');
                previewCardContainer.classList.remove('hidden');
            } else {
                const errorMsg = result.detail || "PDF processing failed.";
                appendLog("ERROR", translations[currentLang].log_error, {
                    reason: errorMsg
                });
                showErrorState("Anomali ve Risk Kontrolü", errorMsg);
            }

        } catch (error) {
            appendLog("ERROR", translations[currentLang].log_network_error, {
                error: error.message
            });
            showErrorState(translations[currentLang].err_network_title, translations[currentLang].err_network_desc);
        } finally {
            submitBtn.disabled = false;
            btnSpinner.classList.add('hidden');
        }
    });

    function showErrorState(title, message) {
        successActions.classList.add('hidden');
        previewCardContainer.classList.add('hidden');
        
        document.getElementById('errorTitle').textContent = title;
        document.getElementById('errorMessage').textContent = message;
        errorState.classList.remove('hidden');
    }
});
