// import { DataTable, DataTableSelectionMultipleChangeEvent } from 'primereact/datatable';
// import './index.css'
// import { Column } from 'primereact/column';
// import { Sidebar } from 'primereact/sidebar';
// import { useEffect, useRef, useState } from 'react';
// import { getCallDetails, getCallHistory } from '../../common/api';
// import { Toast } from 'primereact/toast';
// import { useNavigate } from 'react-router-dom';
// import { pagePaths } from '../../common/constants';
// import { MoonLoader, ScaleLoader } from 'react-spinners';
// import ConversationEval from '../../components/conversation-eval';
// import { Button } from 'primereact/button';
// import { InputText } from 'primereact/inputtext';
// import { Calendar } from 'primereact/calendar';
// import { Dropdown } from 'primereact/dropdown';

// interface HistoryProps {
//   // Add any props here if needed - currently none are required
// }

// interface CallRecord {
//     id?: string;
//     name: string;
//     End_time: string;
//     duration_ms: string;
//     direction: string;
//     from_number: string;
//     to_number: string;
//     call_status: string;
//     recording_api: string;
//     transcript: string;
//     summary: string;
//     [key: string]: any;
// }

// const History: React.FC<HistoryProps> = () => {
//     const navigate = useNavigate();
//     const toast = useRef<Toast>(null);

//     const show = (summary: string, severity: 'error' | 'info' | 'success' = 'error') => {
//         toast.current?.show({ severity, summary, life: 3000 });
//     };

//     const [visible, setVisible] = useState<boolean>(false);
//     const [loading, setLoading] = useState<boolean>(false);
//     const [list, setList] = useState<CallRecord[]>([]);
//     const [filteredList, setFilteredList] = useState<CallRecord[]>([]);
    
//     // Audio states - but with error handling
//     const [audioLoading, setAudioLoading] = useState<boolean>(false);
//     const [audioSrc, setAudioSrc] = useState<string|undefined>();
//     const [audioError, setAudioError] = useState<string | null>(null);
    
//     const [sideBarData, setSideBarData] = useState<any>();
//     const [detailsLoading, setDetailsLoading] = useState<boolean>(false);
//     const [conversationEval, setConversationEval] = useState<any>(null);
    
//     // Filter states
//     const [selectedRecords, setSelectedRecords] = useState<CallRecord[]>([]);
//     const [showFilters, setShowFilters] = useState<boolean>(false);
//     const [searchText, setSearchText] = useState<string>('');
//     const [startDate, setStartDate] = useState<Date | null>(null);
//     const [endDate, setEndDate] = useState<Date | null>(null);
//     const [selectedStatus, setSelectedStatus] = useState<string>('');
//     const [selectedDirection, setSelectedDirection] = useState<string>('');

//     // Filter options
//     const statusOptions = [
//         { label: 'All Status', value: '' },
//         { label: 'Completed', value: 'completed' },
//         { label: 'Failed', value: 'failed' },
//         { label: 'In Progress', value: 'in-progress' },
//         { label: 'Busy', value: 'busy' },
//         { label: 'No Answer', value: 'no-answer' }
//     ];

//     const directionOptions = [
//         { label: 'All Types', value: '' },
//         { label: 'Inbound', value: 'inbound' },
//         { label: 'Outbound', value: 'outbound' }
//     ];

//     // Modified audio fetching with graceful error handling
//     useEffect(() => {
//         const fetchAudioStream = async () => {
//             if (!sideBarData?.recording_api) {
//                 setAudioError("No recording URL available");
//                 return;
//             }

//             try {
//                 setAudioLoading(true);
//                 setAudioError(null);
                
//                 const url: string = sideBarData.recording_api;   
//                 const response = await fetch(url);
                
//                 if (!response.ok) {
//                     // Handle different error types
//                     if (response.status === 404) {
//                         setAudioError("Audio recording not found for this call");
//                     } else if (response.status === 403) {
//                         setAudioError("Access denied to audio recording");
//                     } else {
//                         setAudioError(`Audio not available (Error: ${response.status})`);
//                     }
//                     return;
//                 }

//                 const audioBlob = await response.blob();
                
//                 // Check if the blob is actually audio content
//                 if (audioBlob.size === 0) {
//                     setAudioError("Audio recording is empty");
//                     return;
//                 }
                
//                 const audioUrl = URL.createObjectURL(audioBlob);
//                 setAudioSrc(audioUrl);
//                 setAudioError(null);
                
//             } catch (error) {
//                 console.error("Error streaming audio:", error);
//                 setAudioError("Unable to load audio recording");
//             } finally {
//                 setAudioLoading(false);
//             }
//         };

//         if (sideBarData?.recording_api) {
//             fetchAudioStream();
//         } else {
//             setAudioError("No recording available for this call");
//             setAudioSrc(undefined);
//         }

//         return () => {
//             if (audioSrc) {
//                 URL.revokeObjectURL(audioSrc);
//                 setAudioSrc(undefined);
//             }
//         };
//     }, [sideBarData]);

//     // Apply filters when filter criteria change
//     useEffect(() => {
//         let filtered = [...list];

//         // Text search filter
//         if (searchText) {
//             filtered = filtered.filter(record => 
//                 record.name?.toLowerCase().includes(searchText.toLowerCase()) ||
//                 record.from_number?.includes(searchText) ||
//                 record.to_number?.includes(searchText)
//             );
//         }

//         // Date range filter
//         if (startDate || endDate) {
//             filtered = filtered.filter(record => {
//                 const recordDate = new Date(record.End_time);
//                 if (startDate && recordDate < startDate) return false;
//                 if (endDate && recordDate > endDate) return false;
//                 return true;
//             });
//         }

//         // Status filter
//         if (selectedStatus) {
//             filtered = filtered.filter(record => 
//                 record.call_status?.toLowerCase() === selectedStatus.toLowerCase()
//             );
//         }

//         // Direction filter
//         if (selectedDirection) {
//             filtered = filtered.filter(record => 
//                 record.direction?.toLowerCase() === selectedDirection.toLowerCase()
//             );
//         }

//         setFilteredList(filtered);
//     }, [list, searchText, startDate, endDate, selectedStatus, selectedDirection]);

//     function formatDuration(seconds: number) {
//         const minutes = Math.floor(seconds / 60);
//         const remainingSeconds = seconds % 60;
//         return `${minutes}m ${remainingSeconds}s`;
//     }

//     function formatDurationMillis(milliseconds: number) {
//         const totalSeconds = Math.floor(milliseconds / 1000);
//         return formatDuration(totalSeconds);
//     }

//     const dateTime = (input: number) => {
//         const date = new Date(input);
//         return date.toLocaleString();
//     }

//     useEffect(() => {
//         const user_id = localStorage.getItem("fullName")
//         if (user_id == null) {
//             show("please login first");
//             navigate(pagePaths.signin);
//         } else {
//             setLoading(true);
//             getCallHistory(user_id).then(data => {
//                 const res = data.data.map(({Name, ...d}: { Name: { name: any; }; duration_ms: number; End_time: number; }, index: number) => ({
//                     ...d,
//                     id: `call_${index}`, // Add unique ID for selection
//                     name: Name.name,
//                     duration_ms: formatDurationMillis(d.duration_ms),
//                     End_time: dateTime(d.End_time)
//                 }));
//                 setList(res);
//             }).finally(() => {
//                 setLoading(false);
//             });
//         }
//     }, []);

//     const open = async (rowData: any) => {
//         // Set sidebar data with available information - ALWAYS show transcript/summary
//         setSideBarData({
//             recording_api: rowData.recording_api, 
//             transcript: rowData.transcript, 
//             summary: rowData.summary
//         });
        
//         // Reset states
//         setConversationEval(null);
//         setAudioError(null);
//         setAudioSrc(undefined);
//         setVisible(true);
        
//         // Extract conversation_id from the recording_api URL
//         let conversationId = null;
//         if (rowData.recording_api) {
//             const urlParts = rowData.recording_api.split('/');
//             conversationId = urlParts[urlParts.length - 1];
//             console.log("Extracted conversation ID:", conversationId);
//         }
        
//         // ALWAYS fetch call details regardless of audio availability
//         if (conversationId) {
//             try {
//                 const user_id = localStorage.getItem("fullName");
//                 if (user_id) {
//                     setDetailsLoading(true);
//                     const response = await getCallDetails(user_id, conversationId);
                    
//                     if (response.status <= 299 && response.data) {
//                         // Process conversation eval data
//                         if (response.data.conversation_eval) {
//                             setConversationEval(response.data.conversation_eval);
//                         } else {
//                             setConversationEval(null);
//                         }
                        
//                         // Update sidebar data with fresh transcript/summary if available
//                         // setSideBarData(prev => ({
//                         //     ...prev,
//                         //     transcript: response.data.transcription || prev.transcript,
//                         //     summary: response.data.summary || prev.summary
//                         // }));
//                         setSideBarData((prev: any) => ({
//                         ...prev,
//                         transcript: response.data.transcription || prev?.transcript,
//                         summary: response.data.summary || prev?.summary
//                     }));
//                     } else {
//                         setConversationEval(null);
//                     }
//                 }
//             } catch (error) {
//                 console.error("Error fetching call details:", error);
//                 show("Error fetching conversation evaluation", "info");
//                 setConversationEval(null);
//             } finally {
//                 setDetailsLoading(false);
//             }
//         }
//     };

//     const lockTemplate = (rowData: any) => {
//         return (
//             <span className='view' onClick={() => open(rowData)}>
//                 View Details
//                 <i className="pi pi-arrow-up-right"></i>
//             </span>
//         );
//     };

//     // Clear all filters
//     const clearFilters = () => {
//         setSearchText('');
//         setStartDate(null);
//         setEndDate(null);
//         setSelectedStatus('');
//         setSelectedDirection('');
//         setSelectedRecords([]);
//     };

//     // Toggle filters visibility
//     const toggleFilters = () => {
//         setShowFilters(!showFilters);
//     };

//     // Convert data to CSV format
//     const convertToCSV = (data: CallRecord[]) => {
//         const headers = ['Name', 'Time', 'Duration', 'Type', 'From', 'To', 'Call Status'];
//         const csvContent = [
//             headers.join(','),
//             ...data.map(record => [
//                 `"${record.name || ''}"`,
//                 `"${record.End_time || ''}"`,
//                 `"${record.duration_ms || ''}"`,
//                 `"${record.direction || ''}"`,
//                 `"${record.from_number || ''}"`,
//                 `"${record.to_number || ''}"`,
//                 `"${record.call_status || ''}"`
//             ].join(','))
//         ].join('\n');
        
//         return csvContent;
//     };

//     // Download CSV
//     const downloadCSV = () => {
//         const dataToExport = selectedRecords.length > 0 ? selectedRecords : filteredList;
        
//         if (dataToExport.length === 0) {
//             show("No data to export", "info");
//             return;
//         }

//         const csvContent = convertToCSV(dataToExport);
//         const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
//         const link = document.createElement('a');
        
//         if (link.download !== undefined) {
//             const url = URL.createObjectURL(blob);
//             link.setAttribute('href', url);
//             link.setAttribute('download', `call_history_${new Date().toISOString().split('T')[0]}.csv`);
//             link.style.visibility = 'hidden';
//             document.body.appendChild(link);
//             link.click();
//             document.body.removeChild(link);
//         }
        
//         show(`Exported ${dataToExport.length} records`, "success");
//     };

//     const header = (
//         <div className="table-header">
//             <div className="header-top">
//                 <div className="header-actions">
//                     <Button
//                         label="Filters"
//                         icon={showFilters ? "pi pi-filter-slash" : "pi pi-filter"}
//                         onClick={toggleFilters}
//                         className="filter-toggle-btn"
//                         size="small"
//                         outlined
//                     />
                    
//                     {(searchText || startDate || endDate || selectedStatus || selectedDirection) && (
//                         <Button
//                             label="Clear All"
//                             icon="pi pi-times"
//                             onClick={clearFilters}
//                             className="clear-all-btn"
//                             size="small"
//                             severity="secondary"
//                             outlined
//                         />
//                     )}
//                 </div>
                
//                 <div className="selection-info">
//                     {selectedRecords.length > 0 && (
//                         <span className="selected-count">
//                             {selectedRecords.length} selected
//                         </span>
//                     )}
//                     <span className="total-count">
//                         Showing {filteredList.length} of {list.length} records
//                     </span>
//                 </div>
                
//                 <Button
//                     label={selectedRecords.length > 0 ? `Download Selected (${selectedRecords.length})` : `Download All (${filteredList.length})`}
//                     icon="pi pi-download"
//                     onClick={downloadCSV}
//                     className="download-btn"
//                     disabled={filteredList.length === 0}
//                 />
//             </div>
            
//             {showFilters && (
//                 <div className="filter-section">
//                     <div className="filter-row">
//                         <div className="filter-item">
//                             <label>Search:</label>
//                             <InputText
//                                 value={searchText}
//                                 onChange={(e) => setSearchText(e.target.value)}
//                                 placeholder="Search by name or number..."
//                                 className="search-input"
//                             />
//                         </div>
                        
//                         <div className="filter-item">
//                             <label>From Date:</label>
//                             <Calendar
//                                 value={startDate}
//                                 onChange={(e) => setStartDate(e.value as Date)}
//                                 placeholder="Start date"
//                                 dateFormat="dd/mm/yy"
//                                 showIcon
//                             />
//                         </div>
                        
//                         <div className="filter-item">
//                             <label>To Date:</label>
//                             <Calendar
//                                 value={endDate}
//                                 onChange={(e) => setEndDate(e.value as Date)}
//                                 placeholder="End date"
//                                 dateFormat="dd/mm/yy"
//                                 showIcon
//                             />
//                         </div>
//                     </div>
                    
//                     <div className="filter-row">
//                         <div className="filter-item">
//                             <label>Status:</label>
//                             <Dropdown
//                                 value={selectedStatus}
//                                 options={statusOptions}
//                                 onChange={(e) => setSelectedStatus(e.value)}
//                                 placeholder="Select status"
//                                 className="status-dropdown"
//                             />
//                         </div>
                        
//                         <div className="filter-item">
//                             <label>Type:</label>
//                             <Dropdown
//                                 value={selectedDirection}
//                                 options={directionOptions}
//                                 onChange={(e) => setSelectedDirection(e.value)}
//                                 placeholder="Select type"
//                                 className="direction-dropdown"
//                             />
//                         </div>
                        
//                         <div className="filter-spacer"></div>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );

//     return (
//         <div className="history">
//             <Toast ref={toast} position="bottom-right" />
//             <div className="card">
//                 <DataTable 
//                     value={filteredList} 
//                     tableStyle={{ minWidth: '80rem', maxHeight: '100rem', fontSize: '1.5rem' }} 
//                     size='large' 
//                     resizableColumns 
//                     scrollable 
//                     scrollHeight='65vh'
//                     header={header}
//                     selection={selectedRecords}
//                     onSelectionChange={(e: DataTableSelectionMultipleChangeEvent<CallRecord[]>) => setSelectedRecords(e.value || [])}
//                     dataKey="id"
//                     selectionMode="checkbox"
//                     paginator
//                     rows={10}
//                     rowsPerPageOptions={[5, 10, 25, 50]}
//                     paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
//                     currentPageReportTemplate="{first} to {last} of {totalRecords}"
//                 >
//                     <Column selectionMode="multiple" headerStyle={{ width: '3rem' }}></Column>
//                     <Column field="name" header="Name" sortable></Column>
//                     <Column header="Time" field="End_time" sortable></Column>
//                     <Column header="Duration" field="duration_ms" sortable></Column>
//                     <Column header="Type" field="direction" sortable></Column>
//                     <Column header="From" field="from_number" sortable></Column>
//                     <Column header="To" field="to_number" sortable></Column>
//                     <Column header="Call Status" field="call_status" sortable></Column>
//                     <Column body={lockTemplate} header="Details"></Column>
//                 </DataTable>
//             </div>
            
//             <Sidebar 
//                 visible={visible} 
//                 onHide={() => setVisible(false)}
//                 position='right'
//                 className='sidebar'
//             > 
//                 <h2>Call Details</h2>
//                 <div className='sidebar-text'>
//                     {/* Audio Section - with graceful error handling */}
//                     <div className='audio-section'>
//                         <h3>Recording</h3>
//                         {audioLoading && (
//                             <div className="audio-loading">
//                                 <ScaleLoader height={20} width={2} radius={5} margin={2} color="#979797" />
//                                 <p>Loading audio...</p>
//                             </div>
//                         )}
                        
//                         {audioError && (
//                             <div className="audio-error">
//                                 <i className="pi pi-exclamation-triangle" style={{color: '#ff9800', marginRight: '8px'}}></i>
//                                 <span style={{color: '#666', fontStyle: 'italic'}}>{audioError}</span>
//                             </div>
//                         )}
                        
//                         {audioSrc && !audioError && (
//                             <audio crossOrigin='anonymous' controls src={audioSrc} style={{width: '100%'}}></audio>
//                         )}
//                     </div>
                    
//                     {/* Transcript Section - ALWAYS shows */}
//                     <div className='transcript'>
//                         <h3>Transcript</h3>
//                         <p>
//                             <pre>{sideBarData?.transcript || "Transcript not available"}</pre>  
//                         </p>
//                     </div>
                    
//                     {/* Summary Section - ALWAYS shows */}
//                     <div className='summary'>
//                         <h3>Summary</h3>
//                         <p>
//                             {sideBarData?.summary || "Summary not available"}
//                         </p>
//                     </div>
                    
//                     {/* Conversation Evaluation - ALWAYS shows */}
//                     {detailsLoading ? (
//                         <div className="details-loading">
//                             <ScaleLoader height={20} width={2} radius={5} margin={2} color="#979797" />
//                         </div>
//                     ) : (
//                         <ConversationEval evalData={conversationEval} />
//                     )}
//                 </div>
//             </Sidebar>

//             {loading && (
//                 <div className="loader-overlay">
//                     <MoonLoader size={50} color="black" />
//                 </div>
//             )}
//         </div> 
//     );
// };

// export default History;



import { DataTable, DataTableSelectionMultipleChangeEvent } from 'primereact/datatable';
import './index.css'
import { Column } from 'primereact/column';
import { Sidebar } from 'primereact/sidebar';
import { useEffect, useRef, useState } from 'react';
import { getCallDetails, getCallHistory } from '../../common/api';
import { Toast } from 'primereact/toast';
import { useNavigate } from 'react-router-dom';
import { pagePaths } from '../../common/constants';
import { MoonLoader, ScaleLoader } from 'react-spinners';
import ConversationEval from '../../components/conversation-eval';
import EntityExtraction from '../../components/entity-extraction';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Calendar } from 'primereact/calendar';
import { Dropdown } from 'primereact/dropdown';

interface HistoryProps {
  // Add any props here if needed - currently none are required
}

interface CallRecord {
    id?: string;
    name: string;
    End_time: string;
    duration_ms: string;
    direction: string;
    from_number: string;
    to_number: string;
    call_status: string;
    recording_api: string;
    transcript: string;
    summary: string;
    [key: string]: any;
}

interface CallDetailsResponse {
    transcription: string;
    entity: any;
    conversation_eval: any;
    summary: string;
}

const History: React.FC<HistoryProps> = () => {
    const navigate = useNavigate();
    const toast = useRef<Toast>(null);

    const show = (summary: string, severity: 'error' | 'info' | 'success' = 'error') => {
        toast.current?.show({ severity, summary, life: 3000 });
    };

    const [visible, setVisible] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [list, setList] = useState<CallRecord[]>([]);
    const [filteredList, setFilteredList] = useState<CallRecord[]>([]);
    
    // Audio states - but with error handling
    const [audioLoading, setAudioLoading] = useState<boolean>(false);
    const [audioSrc, setAudioSrc] = useState<string|undefined>();
    const [audioError, setAudioError] = useState<string | null>(null);
    
    const [sideBarData, setSideBarData] = useState<any>();
    const [detailsLoading, setDetailsLoading] = useState<boolean>(false);
    const [conversationEval, setConversationEval] = useState<any>(null);
    const [entityData, setEntityData] = useState<any>(null);
    
    // Filter states
    const [selectedRecords, setSelectedRecords] = useState<CallRecord[]>([]);
    const [showFilters, setShowFilters] = useState<boolean>(false);
    const [searchText, setSearchText] = useState<string>('');
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [selectedStatus, setSelectedStatus] = useState<string>('');
    const [selectedDirection, setSelectedDirection] = useState<string>('');

    // Filter options
    const statusOptions = [
        { label: 'All Status', value: '' },
        { label: 'Completed', value: 'completed' },
        { label: 'Failed', value: 'failed' },
        { label: 'In Progress', value: 'in-progress' },
        { label: 'Busy', value: 'busy' },
        { label: 'No Answer', value: 'no-answer' }
    ];

    const directionOptions = [
        { label: 'All Types', value: '' },
        { label: 'Inbound', value: 'inbound' },
        { label: 'Outbound', value: 'outbound' }
    ];

    // Modified audio fetching with graceful error handling
    useEffect(() => {
        const fetchAudioStream = async () => {
            if (!sideBarData?.recording_api) {
                setAudioError("No recording URL available");
                return;
            }

            try {
                setAudioLoading(true);
                setAudioError(null);
                
                const url: string = sideBarData.recording_api;   
                const response = await fetch(url);
                
                if (!response.ok) {
                    // Handle different error types
                    if (response.status === 404) {
                        setAudioError("Audio recording not found for this call");
                    } else if (response.status === 403) {
                        setAudioError("Access denied to audio recording");
                    } else {
                        setAudioError(`Audio not available (Error: ${response.status})`);
                    }
                    return;
                }

                const audioBlob = await response.blob();
                
                // Check if the blob is actually audio content
                if (audioBlob.size === 0) {
                    setAudioError("Audio recording is empty");
                    return;
                }
                
                const audioUrl = URL.createObjectURL(audioBlob);
                setAudioSrc(audioUrl);
                setAudioError(null);
                
            } catch (error) {
                console.error("Error streaming audio:", error);
                setAudioError("Unable to load audio recording");
            } finally {
                setAudioLoading(false);
            }
        };

        if (sideBarData?.recording_api) {
            fetchAudioStream();
        } else {
            setAudioError("No recording available for this call");
            setAudioSrc(undefined);
        }

        return () => {
            if (audioSrc) {
                URL.revokeObjectURL(audioSrc);
                setAudioSrc(undefined);
            }
        };
    }, [sideBarData]);

    // Apply filters when filter criteria change
    useEffect(() => {
        let filtered = [...list];

        // Text search filter
        if (searchText) {
            filtered = filtered.filter(record => 
                record.name?.toLowerCase().includes(searchText.toLowerCase()) ||
                record.from_number?.includes(searchText) ||
                record.to_number?.includes(searchText)
            );
        }

        // Date range filter
        if (startDate || endDate) {
            filtered = filtered.filter(record => {
                const recordDate = new Date(record.End_time);
                if (startDate && recordDate < startDate) return false;
                if (endDate && recordDate > endDate) return false;
                return true;
            });
        }

        // Status filter
        if (selectedStatus) {
            filtered = filtered.filter(record => 
                record.call_status?.toLowerCase() === selectedStatus.toLowerCase()
            );
        }

        // Direction filter
        if (selectedDirection) {
            filtered = filtered.filter(record => 
                record.direction?.toLowerCase() === selectedDirection.toLowerCase()
            );
        }

        setFilteredList(filtered);
    }, [list, searchText, startDate, endDate, selectedStatus, selectedDirection]);

    function formatDuration(seconds: number) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    }

    function formatDurationMillis(milliseconds: number) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        return formatDuration(totalSeconds);
    }

    const dateTime = (input: number) => {
        const date = new Date(input);
        return date.toLocaleString();
    }

    useEffect(() => {
        const user_id = localStorage.getItem("fullName")
        if (user_id == null) {
            show("please login first");
            navigate(pagePaths.signin);
        } else {
            setLoading(true);
            getCallHistory(user_id).then(data => {
                const res = data.data.map(({Name, ...d}: { Name: { name: any; }; duration_ms: number; End_time: number; }, index: number) => ({
                    ...d,
                    id: `call_${index}`, // Add unique ID for selection
                    name: Name.name,
                    duration_ms: formatDurationMillis(d.duration_ms),
                    End_time: dateTime(d.End_time)
                }));
                setList(res);
            }).finally(() => {
                setLoading(false);
            });
        }
    }, []);

    const open = async (rowData: any) => {
        // Set sidebar data with available information - ALWAYS show transcript/summary
        setSideBarData({
            recording_api: rowData.recording_api, 
            transcript: rowData.transcript, 
            summary: rowData.summary
        });
        
        // Reset states
        setConversationEval(null);
        setEntityData(null);
        setAudioError(null);
        setAudioSrc(undefined);
        setVisible(true);
        
        // Extract conversation_id from the recording_api URL
        let conversationId = null;
        if (rowData.recording_api) {
            const urlParts = rowData.recording_api.split('/');
            conversationId = urlParts[urlParts.length - 1];
            console.log("Extracted conversation ID:", conversationId);
        }
        
        // ALWAYS fetch call details regardless of audio availability
        if (conversationId) {
            try {
                const user_id = localStorage.getItem("fullName");
                if (user_id) {
                    setDetailsLoading(true);
                    const response = await getCallDetails(user_id, conversationId);
                    
                    if (response.status <= 299 && response.data) {
                        const callDetails: CallDetailsResponse = response.data;
                        
                        // Process conversation eval data
                        if (callDetails.conversation_eval) {
                            setConversationEval(callDetails.conversation_eval);
                        } else {
                            setConversationEval(null);
                        }
                        
                        // Process entity data
                        if (callDetails.entity) {
                            setEntityData(callDetails.entity);
                        } else {
                            setEntityData(null);
                        }
                        
                        // Update sidebar data with fresh transcript/summary if available
                        setSideBarData((prev: any) => ({
                            ...prev,
                            transcript: callDetails.transcription || prev?.transcript,
                            summary: callDetails.summary || prev?.summary
                        }));
                    } else {
                        setConversationEval(null);
                        setEntityData(null);
                    }
                }
            } catch (error) {
                console.error("Error fetching call details:", error);
                show("Error fetching call details", "info");
                setConversationEval(null);
                setEntityData(null);
            } finally {
                setDetailsLoading(false);
            }
        }
    };

    const lockTemplate = (rowData: any) => {
        return (
            <span className='view' onClick={() => open(rowData)}>
                View Details
                <i className="pi pi-arrow-up-right"></i>
            </span>
        );
    };

    // Clear all filters
    const clearFilters = () => {
        setSearchText('');
        setStartDate(null);
        setEndDate(null);
        setSelectedStatus('');
        setSelectedDirection('');
        setSelectedRecords([]);
    };

    // Toggle filters visibility
    const toggleFilters = () => {
        setShowFilters(!showFilters);
    };

    // Convert data to CSV format
    const convertToCSV = (data: CallRecord[]) => {
        const headers = ['Name', 'Time', 'Duration', 'Type', 'From', 'To', 'Call Status'];
        const csvContent = [
            headers.join(','),
            ...data.map(record => [
                `"${record.name || ''}"`,
                `"${record.End_time || ''}"`,
                `"${record.duration_ms || ''}"`,
                `"${record.direction || ''}"`,
                `"${record.from_number || ''}"`,
                `"${record.to_number || ''}"`,
                `"${record.call_status || ''}"`
            ].join(','))
        ].join('\n');
        
        return csvContent;
    };

    // Download CSV
    const downloadCSV = () => {
        const dataToExport = selectedRecords.length > 0 ? selectedRecords : filteredList;
        
        if (dataToExport.length === 0) {
            show("No data to export", "info");
            return;
        }

        const csvContent = convertToCSV(dataToExport);
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `call_history_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        show(`Exported ${dataToExport.length} records`, "success");
    };

    const header = (
        <div className="table-header">
            <div className="header-top">
                <div className="header-actions">
                    <Button
                        label="Filters"
                        icon={showFilters ? "pi pi-filter-slash" : "pi pi-filter"}
                        onClick={toggleFilters}
                        className="filter-toggle-btn"
                        size="small"
                        outlined
                    />
                    
                    {(searchText || startDate || endDate || selectedStatus || selectedDirection) && (
                        <Button
                            label="Clear All"
                            icon="pi pi-times"
                            onClick={clearFilters}
                            className="clear-all-btn"
                            size="small"
                            severity="secondary"
                            outlined
                        />
                    )}
                </div>
                
                <div className="selection-info">
                    {selectedRecords.length > 0 && (
                        <span className="selected-count">
                            {selectedRecords.length} selected
                        </span>
                    )}
                    <span className="total-count">
                        Showing {filteredList.length} of {list.length} records
                    </span>
                </div>
                
                <Button
                    label={selectedRecords.length > 0 ? `Download Selected (${selectedRecords.length})` : `Download All (${filteredList.length})`}
                    icon="pi pi-download"
                    onClick={downloadCSV}
                    className="download-btn"
                    disabled={filteredList.length === 0}
                />
            </div>
            
            {showFilters && (
                <div className="filter-section">
                    <div className="filter-row">
                        <div className="filter-item">
                            <label>Search:</label>
                            <InputText
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                                placeholder="Search by name or number..."
                                className="search-input"
                            />
                        </div>
                        
                        <div className="filter-item">
                            <label>From Date:</label>
                            <Calendar
                                value={startDate}
                                onChange={(e) => setStartDate(e.value as Date)}
                                placeholder="Start date"
                                dateFormat="dd/mm/yy"
                                showIcon
                            />
                        </div>
                        
                        <div className="filter-item">
                            <label>To Date:</label>
                            <Calendar
                                value={endDate}
                                onChange={(e) => setEndDate(e.value as Date)}
                                placeholder="End date"
                                dateFormat="dd/mm/yy"
                                showIcon
                            />
                        </div>
                    </div>
                    
                    <div className="filter-row">
                        <div className="filter-item">
                            <label>Status:</label>
                            <Dropdown
                                value={selectedStatus}
                                options={statusOptions}
                                onChange={(e) => setSelectedStatus(e.value)}
                                placeholder="Select status"
                                className="status-dropdown"
                            />
                        </div>
                        
                        <div className="filter-item">
                            <label>Type:</label>
                            <Dropdown
                                value={selectedDirection}
                                options={directionOptions}
                                onChange={(e) => setSelectedDirection(e.value)}
                                placeholder="Select type"
                                className="direction-dropdown"
                            />
                        </div>
                        
                        <div className="filter-spacer"></div>
                    </div>
                </div>
            )}
        </div>
    );

    return (
        <div className="history">
            <Toast ref={toast} position="bottom-right" />
            <div className="card">
                <DataTable 
                    value={filteredList} 
                    tableStyle={{ minWidth: '80rem', maxHeight: '100rem', fontSize: '1.5rem' }} 
                    size='large' 
                    resizableColumns 
                    scrollable 
                    scrollHeight='65vh'
                    header={header}
                    selection={selectedRecords}
                    onSelectionChange={(e: DataTableSelectionMultipleChangeEvent<CallRecord[]>) => setSelectedRecords(e.value || [])}
                    dataKey="id"
                    selectionMode="checkbox"
                    paginator
                    rows={10}
                    rowsPerPageOptions={[5, 10, 25, 50]}
                    paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
                    currentPageReportTemplate="{first} to {last} of {totalRecords}"
                >
                    <Column selectionMode="multiple" headerStyle={{ width: '3rem' }}></Column>
                    <Column field="name" header="Name" sortable></Column>
                    <Column header="Time" field="End_time" sortable></Column>
                    <Column header="Duration" field="duration_ms" sortable></Column>
                    <Column header="Type" field="direction" sortable></Column>
                    <Column header="From" field="from_number" sortable></Column>
                    <Column header="To" field="to_number" sortable></Column>
                    <Column header="Call Status" field="call_status" sortable></Column>
                    <Column body={lockTemplate} header="Details"></Column>
                </DataTable>
            </div>
            
            <Sidebar 
                visible={visible} 
                onHide={() => setVisible(false)}
                position='right'
                className='sidebar'
            > 
                <h2>Recording/Transcript</h2>
                <div className='sidebar-text'>
                    {/* Audio Section - with graceful error handling */}
                    <div className='audio-section'>
                        <h3>Recording</h3>
                        {audioLoading && (
                            <div className="audio-loading">
                                <ScaleLoader height={20} width={2} radius={5} margin={2} color="#979797" />
                                <p>Loading audio...</p>
                            </div>
                        )}
                        
                        {audioError && (
                            <div className="audio-error">
                                <i className="pi pi-exclamation-triangle" style={{color: '#ff9800', marginRight: '8px'}}></i>
                                <span style={{color: '#666', fontStyle: 'italic'}}>{audioError}</span>
                            </div>
                        )}
                        
                        {audioSrc && !audioError && (
                            <audio crossOrigin='anonymous' controls src={audioSrc} style={{width: '100%'}}></audio>
                        )}
                    </div>
                    
                    {/* Transcript Section - ALWAYS shows */}
                    <div className='transcript'>
                        <h3>Transcript</h3>
                        <p>
                            <pre>{sideBarData?.transcript || "Transcript not available"}</pre>  
                        </p>
                    </div>
                    
                    {/* Summary Section - ALWAYS shows */}
                    <div className='summary'>
                        <h3>Summary</h3>
                        <p>
                            {sideBarData?.summary || "Summary not available"}
                        </p>
                    </div>
                    
                    {/* Conversation Evaluation - ALWAYS shows */}
                    {detailsLoading ? (
                        <div className="details-loading">
                            <ScaleLoader height={20} width={2} radius={5} margin={2} color="#979797" />
                        </div>
                    ) : (
                        <ConversationEval evalData={conversationEval} />
                    )}
                    
                    {/* Entity Extraction - NEW SECTION */}
                    {detailsLoading ? (
                        <div className="details-loading">
                            <ScaleLoader height={20} width={2} radius={5} margin={2} color="#979797" />
                        </div>
                    ) : (
                        <EntityExtraction entities={entityData} />
                    )}
                </div>
            </Sidebar>

            {loading && (
                <div className="loader-overlay">
                    <MoonLoader size={50} color="black" />
                </div>
            )}
        </div> 
    );
};

export default History;