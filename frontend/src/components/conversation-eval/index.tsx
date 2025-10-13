import React from 'react';
import './index.css';

interface ConversationEvalProps {
  evalData: {
    result?: string | any;
    [key: string]: any;
  } | null;
}

interface EvalCategory {
  score: number;
  feedback: string;
}

interface ParsedEvalData {
  clarity?: EvalCategory;
  fluency?: EvalCategory;
  coherence?: EvalCategory;
  engagement?: EvalCategory;
  vocabulary?: EvalCategory;
  listening?: EvalCategory;
  summary?: string;
  tip?: string;
  [key: string]: EvalCategory | string | undefined;
}

// Helper function to parse the evaluation data from the result string
const parseEvalData = (result: string | any): ParsedEvalData | null => {
  try {
    // If result is already an object, return it directly
    if (typeof result !== 'string' && result !== null && typeof result === 'object') {
      return result as ParsedEvalData;
    }

    // If result is a string, try to parse it
    if (typeof result === 'string') {
      const resultText = result;
      
      // Clean up the result string by removing extra braces
      const cleanedResult = resultText
        .replace(/\{\{\{\{/g, '{')
        .replace(/\}\}\}\}/g, '}')
        .replace(/\{\{/g, '{')
        .replace(/\}\}/g, '}')
        .replace(/\\n/g, '\n')
        .replace(/\\"/g, '"');
      
      // Try to parse as JSON
      try {
        return JSON.parse(cleanedResult) as ParsedEvalData;
      } catch (e) {
        // If direct parsing fails, try adding outer braces
        try {
          return JSON.parse('{' + cleanedResult + '}') as ParsedEvalData;
        } catch (e2) {
          // Use regex to extract key data points if JSON parsing fails
          const jsonData = {} as ParsedEvalData;
          
          // Extract scores and feedback using regex
          const categories = ['clarity', 'fluency', 'coherence', 'engagement', 'vocabulary', 'listening'];
          categories.forEach(category => {
            const scoreMatch = resultText.match(new RegExp(`"${category}":\\s*{\\s*"score":\\s*(\\d+)`, 'i'));
            const feedbackMatch = resultText.match(new RegExp(`"${category}":\\s*{\\s*"score":\\s*\\d+,\\s*"feedback":\\s*"([^"]*)"`, 'i'));
            
            if (scoreMatch && feedbackMatch) {
              jsonData[category] = {
                score: parseInt(scoreMatch[1]),
                feedback: feedbackMatch[1]
              };
            }
          });

          // Extract summary and tip
          const summaryMatch = resultText.match(/"summary":\s*"([^"]*)"/);
          if (summaryMatch) {
            jsonData.summary = summaryMatch[1];
          }
          
          const tipMatch = resultText.match(/"tip":\s*"([^"]*)"/);
          if (tipMatch) {
            jsonData.tip = tipMatch[1];
          }
          
          // If we found at least some data, return it
          if (Object.keys(jsonData).length > 0) {
            return jsonData;
          }
        }
      }
    }
    
    return null;
  } catch (error) {
    console.error("Error parsing evaluation data:", error);
    return null;
  }
};

const ConversationEval: React.FC<ConversationEvalProps> = ({ evalData }) => {
  if (!evalData) {
    return (
      <div className="conversation-eval">
        <h3>Conversation Evaluation</h3>
        <div className="no-data">No evaluation data available for this call</div>
      </div>
    );
  }

  // Handle the case where evalData has a result property
  const resultData = evalData.result;

  if (!resultData) {
    return (
      <div className="conversation-eval">
        <h3>Conversation Evaluation</h3>
        <div className="no-data">No evaluation result available</div>
      </div>
    );
  }

  // Parse the evaluation data
  const parsedData = parseEvalData(resultData);
  
  if (!parsedData) {
    return (
      <div className="conversation-eval">
        <h3>Conversation Evaluation</h3>
        <div className="no-data">Error formatting evaluation data</div>
      </div>
    );
  }

  // Extract categories that have score and feedback
  const categories = ['clarity', 'fluency', 'coherence', 'engagement', 'vocabulary', 'listening'].filter(
    category => parsedData[category] && typeof parsedData[category] === 'object'
  );

  // Check if all scores are 0 (indicating insufficient data)
  const hasZeroScores = categories.length > 0 && 
    categories.every(category => (parsedData[category] as EvalCategory).score === 0);

  if (hasZeroScores) {
    return (
      <div className="conversation-eval">
        <h3>Conversation Evaluation</h3>
        <div className="insufficient-data">
          <h4>Insufficient Data</h4>
          <p>{parsedData.summary || "There is not enough user data available to evaluate the communication skills."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-eval">
      <h3>Conversation Evaluation</h3>
      
      <div className="eval-scores">
        {categories.map(category => (
          <div key={category} className="score-card">
            <div className="score-header">
              <div className="score-title">{category.charAt(0).toUpperCase() + category.slice(1)}</div>
              <div className="score-value">
                <div className="score-number">{(parsedData[category] as EvalCategory).score}</div>
                <div className="score-stars">
                  {[1, 2, 3, 4, 5].map(star => (
                    <span key={star} className={`score-star ${star <= (parsedData[category] as EvalCategory).score ? 'filled' : ''}`}>
                      ★
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <div className="score-feedback">{(parsedData[category] as EvalCategory).feedback}</div>
          </div>
        ))}
      </div>
      
      {parsedData.summary && (
        <div className="eval-summary">
          <h4>Summary</h4>
          <p>{parsedData.summary}</p>
        </div>
      )}
      
      {parsedData.tip && parsedData.tip !== "Please ensure the user responds in the conversation so that their communication skills can be properly evaluated." && (
        <div className="eval-tip">
          <h4>Improvement Tip</h4>
          <p>{parsedData.tip}</p>
        </div>
      )}
    </div>
  );
};

export default ConversationEval;