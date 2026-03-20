import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface DraftTransaction {
    id?: number;
    date: string;
    amount: number;
    category_id: number;
    expense_type_id: number;
    shop: string;
    content: string;
    payer: string;
    description: string;
    source_type: string;
}

export const useImportStore = defineStore('import', () => {
    const originalFile = ref<File | null>(null);
    const pdfUrl = ref<string>('');
    const pendingTransactions = ref<DraftTransaction[]>([]);
    const isAnalyzing = ref<boolean>(false);

    const setFile = (file: File) => {
        originalFile.value = file;
        if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value);
        pdfUrl.value = URL.createObjectURL(file);
    };

    const clearDrafts = () => {
        pendingTransactions.value = [];
        originalFile.value = null;
        if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value);
        pdfUrl.value = '';
    };

    const analyzePdf = async () => {
        if (!originalFile.value) return;
        
        isAnalyzing.value = true;
        try {
            const formData = new FormData();
            formData.append('file', originalFile.value);
            
            const response = await api.post('/receipts/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            pendingTransactions.value = response.data;
        } catch (error) {
            console.error('Failed to analyze PDF:', error);
            throw error;
        } finally {
            isAnalyzing.value = false;
        }
    };

    const registerAll = async () => {
        if (pendingTransactions.value.length === 0) return;
        isAnalyzing.value = true;
        try {
            await api.post('/transactions/bulk', pendingTransactions.value);
            clearDrafts();
        } catch (error) {
            console.error('Failed to save drafted transactions:', error);
            throw error;
        } finally {
            isAnalyzing.value = false;
        }
    };

    return {
        originalFile,
        pdfUrl,
        pendingTransactions,
        isAnalyzing,
        setFile,
        analyzePdf,
        clearDrafts,
        registerAll
    }
});
