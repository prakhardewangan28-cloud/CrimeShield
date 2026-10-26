import React, { useEffect, useRef, useState, useMemo } from 'react';
import cytoscape, { type Core, type EventObject } from 'cytoscape';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Filter, Layers, Info } from 'lucide-react';
import type { Case, Connection } from '../../types';

interface NetworkGraphProps {
  cases: Case[];
  connections: Connection[];
  onSelectCase?: (caseItem: Case) => void;
  onSelectConnection?: (connection: Connection) => void;
  isLoading?: boolean;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  cases,
  connections,
  onSelectCase,
  onSelectConnection,
  isLoading = false
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<number | null>(null);

  // Filter connections by type if selected
  const filteredConnections = useMemo(() => {
    if (selectedType === 'all') return connections;
    return connections.filter((c) => c.connection_type.toLowerCase().includes(selectedType.toLowerCase()));
  }, [connections, selectedType]);

  useEffect(() => {
    if (!containerRef.current) return;

    // Build elements
    const elements: cytoscape.ElementDefinition[] = [];

    // Add nodes
    cases.forEach((c) => {
      elements.push({
        group: 'nodes',
        data: {
          id: `case_${c.id}`,
          caseId: c.id,
          label: c.case_code,
          title: c.title,
          status: c.status
        }
      });
    });

    // Add edges
    filteredConnections.forEach((conn) => {
      elements.push({
        group: 'edges',
        data: {
          id: `conn_${conn.id}`,
          connId: conn.id,
          source: `case_${conn.case_id_1}`,
          target: `case_${conn.case_id_2}`,
          connection_type: conn.connection_type,
          connection_value: conn.connection_value,
          review_status: conn.review_status,
          explanation: conn.explanation
        }
      });
    });

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#F1F5F9',
            'font-family': 'JetBrains Mono, monospace',
            'font-size': '11px',
            'font-weight': 600,
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'background-color': '#111C2D',
            'border-width': 2.5,
            'border-color': '#22D3EE',
            'width': 42,
            'height': 42,
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': 0.2
          }
        },
        {
          selector: 'node[status = "open"]',
          style: {
            'border-color': '#22D3EE',
            'background-color': '#082F49'
          }
        },
        {
          selector: 'node[status = "under_review"]',
          style: {
            'border-color': '#F59E0B',
            'background-color': '#451A03'
          }
        },
        {
          selector: 'node[status = "closed"]',
          style: {
            'border-color': '#64748B',
            'background-color': '#1E293B'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#FFFFFF',
            'border-width': 4,
            'width': 50,
            'height': 50
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2.5,
            'line-color': '#3B82F6',
            'curve-style': 'bezier',
            'opacity': 0.85
          }
        },
        {
          selector: 'edge[connection_type *= "person"]',
          style: {
            'line-color': '#8B5CF6',
            'line-style': 'dashed'
          }
        },
        {
          selector: 'edge[connection_type *= "location"]',
          style: {
            'line-color': '#22D3EE',
            'line-style': 'solid'
          }
        },
        {
          selector: 'edge[connection_type *= "phone"]',
          style: {
            'line-color': '#22C55E',
            'line-style': 'dotted'
          }
        },
        {
          selector: 'edge[review_status = "confirmed_for_review"]',
          style: {
            'width': 4,
            'opacity': 1
          }
        },
        {
          selector: 'edge[review_status = "dismissed"]',
          style: {
            'opacity': 0.3,
            'width': 1.5,
            'line-color': '#475569'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'width': 5,
            'line-color': '#FFFFFF',
            'opacity': 1
          }
        }
      ],
      layout: {
        name: cases.length <= 6 ? 'circle' : 'cose',
        animate: false,
        padding: 50
      },
      minZoom: 0.3,
      maxZoom: 3
    });

    // Node click
    cy.on('tap', 'node', (evt: EventObject) => {
      const node = evt.target;
      const caseId = node.data('caseId');
      setSelectedNodeId(caseId);
      setSelectedEdgeId(null);
      const foundCase = cases.find((c) => c.id === caseId);
      if (foundCase && onSelectCase) {
        onSelectCase(foundCase);
      }
    });

    // Edge click
    cy.on('tap', 'edge', (evt: EventObject) => {
      const edge = evt.target;
      const connId = edge.data('connId');
      setSelectedEdgeId(connId);
      setSelectedNodeId(null);
      const foundConn = connections.find((c) => c.id === connId);
      if (foundConn && onSelectConnection) {
        onSelectConnection(foundConn);
      }
    });

    // Background click
    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNodeId(null);
        setSelectedEdgeId(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [cases, filteredConnections, onSelectCase, onSelectConnection]);

  // Controls
  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 40);
  const handleResetLayout = () => {
    cyRef.current?.layout({ name: cases.length <= 6 ? 'circle' : 'cose', animate: true }).run();
  };

  return (
    <div className="relative w-full h-[600px] bg-[#0A101D] border border-[#1E293B] rounded-2xl overflow-hidden shadow-2xl flex flex-col">
      {/* Top Action Bar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        {/* Filter Pills */}
        <div className="pointer-events-auto flex items-center gap-1.5 p-1 rounded-xl bg-[#0D1422]/90 border border-[#1E293B] backdrop-blur-md shadow-lg">
          <span className="text-[11px] font-semibold text-[#94A3B8] px-2 flex items-center gap-1">
            <Filter className="w-3 h-3 text-cyan-400" /> Filter:
          </span>
          {[
            { id: 'all', label: 'All Links' },
            { id: 'person', label: 'Person' },
            { id: 'location', label: 'Location' },
            { id: 'phone', label: 'Phone' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedType(tab.id)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all ${
                selectedType === tab.id
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'text-[#94A3B8] hover:text-white hover:bg-[#1E293B]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Zoom & View Controls */}
        <div className="pointer-events-auto flex items-center gap-1 p-1 rounded-xl bg-[#0D1422]/90 border border-[#1E293B] backdrop-blur-md shadow-lg">
          <button
            onClick={handleZoomIn}
            title="Zoom In"
            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B] transition-colors"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            title="Zoom Out"
            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B] transition-colors"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleFit}
            title="Fit to Screen"
            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B] transition-colors"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetLayout}
            title="Re-layout Nodes"
            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E293B] transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Canvas */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-[#080D18]/80 backdrop-blur-sm flex items-center justify-center z-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
            <p className="text-sm font-medium text-cyan-300">Rendering Criminal Network Graph...</p>
          </div>
        </div>
      )}

      {/* Bottom Legend */}
      <div className="absolute bottom-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        <div className="pointer-events-auto flex flex-wrap items-center gap-4 px-4 py-2 rounded-xl bg-[#0D1422]/90 border border-[#1E293B] backdrop-blur-md text-xs shadow-lg">
          <div className="flex items-center gap-1.5 font-semibold text-[#94A3B8]">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Legend:</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-3 rounded-full border-2 border-cyan-400 bg-cyan-950" />
              Open Case
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-3 rounded-full border-2 border-amber-400 bg-amber-950" />
              Under Review
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-3 rounded-full border-2 border-slate-500 bg-slate-800" />
              Closed
            </span>
          </div>

          <div className="w-px h-4 bg-[#1E293B]" />

          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-4 h-0.5 bg-violet-400 border-t border-dashed border-violet-400" />
              Person Match
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-4 h-0.5 bg-cyan-400" />
              Location Match
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-4 h-0.5 bg-emerald-400 border-t border-dotted border-emerald-400" />
              Phone Match
            </span>
          </div>
        </div>

        {/* Tip */}
        <div className="pointer-events-auto hidden md:flex items-center gap-1.5 text-[11px] text-[#94A3B8] px-3 py-1.5 rounded-lg bg-[#0D1422]/90 border border-[#1E293B] backdrop-blur-md">
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          <span>Click any node or link to inspect details</span>
        </div>
      </div>
    </div>
  );
};
