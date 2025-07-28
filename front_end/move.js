import { useState, createElement } from 'react';

export default function SfenNavigator({ data }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [modePv, setModePv] = useState(false);
  const [history, setHistory] = useState([{ index: 0, id: data.nodes[0].id }]);

  const currentNode = data.nodes.find(n => n.index === currentIndex);
  const nextOptions = currentNode?.next_ids?.map(id => data.nodes.find(n => n.id === id));

  const goTo = (newIndex, nodeId) => {
    setCurrentIndex(newIndex);
    setHistory(prev => [...prev, { index: newIndex, id: nodeId }]);
  };

  const goPrevious = () => {
    if (history.length > 1) {
      const newHistory = [...history];
      newHistory.pop();
      const last = newHistory[newHistory.length - 1];
      setHistory(newHistory);
      setCurrentIndex(last.index);
    }
  };

  const goNext = () => {
    if (!nextOptions || nextOptions.length === 0) return;

    if (nextOptions.length === 1) {
      goTo(nextOptions[0].index, nextOptions[0].id);
    } else {
      alert("Multiple next moves. Please select from the list below.");
    }
  };

  const goPv = () => {
    const pv = currentNode?.pv || [];
    if (pv.length > 1) {
      alert("PV Mode active. Navigating PV path.");
      const nextSfen = pv[1];
      const nextNode = data.nodes.find(n => n.sfen === nextSfen);
      if (nextNode) {
        goTo(nextNode.index, nextNode.id);
      }
    }
  };

  const handleNext = () => {
    if (modePv) goPv();
    else goNext();
  };

  const container = createElement("div", { className: "p-4 space-y-4" },
    createElement("div", { className: "text-sm font-mono whitespace-pre-wrap break-words" },
      createElement("strong", null, "SFEN:"),
      createElement("br"),
      currentNode?.sfen || 'No data'
    ),
    createElement("div", { className: "text-sm font-mono" },
      createElement("strong", null, "CP:"),
      typeof currentNode?.cp === 'number' ? ` ${currentNode.cp}` : ' N/A'
    ),
    createElement("div", { className: "space-x-2" },
      createElement("button", {
        onClick: goPrevious,
        className: "px-4 py-2 rounded bg-gray-300"
      }, "Previous"),
      createElement("button", {
        onClick: handleNext,
        className: "px-4 py-2 rounded bg-blue-400 text-white"
      }, "Next"),
      createElement("label", { className: "ml-4" },
        createElement("input", {
          type: "checkbox",
          checked: modePv,
          onChange: (e) => setModePv(e.target.checked),
          className: "mr-2"
        }),
        "PV Mode"
      )
    ),
    nextOptions?.length > 1 && createElement("div", { className: "border p-2 rounded" },
      createElement("div", null, createElement("strong", null, "Select Next Move:")),
      createElement("ul", { className: "list-disc list-inside" },
        ...nextOptions.map((node) =>
          createElement("li", { key: node.id },
            createElement("button", {
              onClick: () => goTo(node.index, node.id),
              className: "text-blue-600 underline"
            }, `Move: ${node.move}, Index: ${node.index}`)
          )
        )
      )
    )
  );

  return container;
}
