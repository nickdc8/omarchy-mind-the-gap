import QtQuick
import QtQuick.Window
import Quickshell
import Quickshell.Io
import qs.Ui

BarWidget {
    id: root
    moduleName: "nickdc8.mind-the-gap"
    readonly property string scriptPath: decodeURIComponent(Qt.resolvedUrl("mind_the_gap.py").toString().slice(7))
    property bool hasGaps: false
    function refreshGaps() {
        if (!probe.running) probe.running = true
    }
    Component.onCompleted: refreshGaps()
    implicitWidth: hasGaps ? button.implicitWidth : 0
    implicitHeight: root.barSize
    HoverHandler {
        id: barHover
        onHoveredChanged: if (hovered) root.refreshGaps()
        parent: root.Window.window ? root.Window.window.contentItem : root
    }
    WidgetButton {
        id: button
        anchors.fill: parent
        bar: root.bar
        visible: root.hasGaps
        text: "Close gaps"
        tooltipText: "Mind the Gap — close empty desktop gaps"
        opacity: barHover.hovered ? 1 : 0
        enabled: opacity > 0 && !worker.running
        horizontalMargin: 8
        fixedHeight: root.barSize
        onPressed: worker.running = true
    }
    Timer {
        interval: 1000
        running: barHover.hovered
        repeat: true
        onTriggered: root.refreshGaps()
    }
    Process {
        id: probe
        command: ["python3", root.scriptPath, "--status"]
        stdout: StdioCollector {
            onStreamFinished: root.hasGaps = text.trim() === "true"
        }
    }
    Process {
        id: worker
        command: ["python3", root.scriptPath, "--once"]
        onExited: root.refreshGaps()
        stderr: StdioCollector { onStreamFinished: { if (text) console.warn("Mind the Gap: " + text) } }
    }
}
