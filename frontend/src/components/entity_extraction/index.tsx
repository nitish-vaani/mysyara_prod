import React from 'react';
import './index.css';

interface EntityData {
  text: string;
  value: string;
  confidence: string;
}

interface EntityExtractionProps {
  entities: Record<string, EntityData> | null;
}

const EntityExtraction: React.FC<EntityExtractionProps> = ({ entities }) => {
  if (!entities || typeof entities !== 'object') {
    return (
      <div className="entity-extraction">
        <h3>Extracted Information</h3>
        <div className="no-data">No entity data available for this call</div>
      </div>
    );
  }

  // Check if entities is empty or all values are "Not Mentioned"
  const entityEntries = Object.entries(entities);
  const hasValidEntities = entityEntries.some(([, data]) => 
    data.value && data.value !== "Not Mentioned"
  );

  if (!hasValidEntities) {
    return (
      <div className="entity-extraction">
        <h3>Extracted Information</h3>
        <div className="no-data">No entities were extracted from this conversation</div>
      </div>
    );
  }

  const getConfidenceColor = (confidence: string): string => {
    switch (confidence?.toLowerCase()) {
      case 'high':
        return '#4CAF50'; // Green
      case 'medium':
        return '#FF9800'; // Orange
      case 'low':
        return '#f44336'; // Red
      default:
        return '#9E9E9E'; // Gray
    }
  };

  const getConfidenceIcon = (confidence: string): string => {
    switch (confidence?.toLowerCase()) {
      case 'high':
        return 'pi pi-check-circle';
      case 'medium':
        return 'pi pi-exclamation-triangle';
      case 'low':
        return 'pi pi-times-circle';
      default:
        return 'pi pi-question-circle';
    }
  };

  const formatFieldName = (fieldName: string): string => {
    return fieldName
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/\b\w/g, l => l.toUpperCase())
      .trim();
  };

  return (
    <div className="entity-extraction">
      <h3>Extracted Information</h3>
      
      <div className="entity-grid">
        {entityEntries.map(([fieldName, data]) => {
          // Skip fields with "Not Mentioned" values
          if (!data.value || data.value === "Not Mentioned") {
            return null;
          }

          return (
            <div key={fieldName} className="entity-card">
              <div className="entity-header">
                <h4 className="entity-field-name">
                  {formatFieldName(fieldName)}
                </h4>
                <div 
                  className="confidence-badge"
                  style={{ 
                    backgroundColor: getConfidenceColor(data.confidence),
                    color: 'white'
                  }}
                >
                  <i className={getConfidenceIcon(data.confidence)}></i>
                  <span>{data.confidence || 'N/A'}</span>
                </div>
              </div>
              
              <div className="entity-value">
                <strong>{data.value}</strong>
              </div>
              
              {data.text && data.text !== "NA" && data.text !== "Not Mentioned" && (
                <div className="entity-source">
                  <span className="source-label">From transcript:</span>
                  <span className="source-text">"{data.text}"</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Show not mentioned fields in a separate section */}
      <div className="not-extracted-section">
        <h4>Information Not Captured</h4>
        <div className="not-extracted-items">
          {entityEntries
            .filter(([, data]) => !data.value || data.value === "Not Mentioned")
            .map(([fieldName]) => (
              <span key={fieldName} className="not-extracted-item">
                {formatFieldName(fieldName)}
              </span>
            ))}
        </div>
      </div>
    </div>
  );
};

export default EntityExtraction;