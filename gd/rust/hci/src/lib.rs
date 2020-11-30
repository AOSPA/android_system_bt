//! Host Controller Interface (HCI)

/// HCI errors
pub mod error;

/// HCI layer facade service
pub mod facade;

use gddi::{module, provides};
use tokio::sync::mpsc;
use tokio::sync::mpsc::{channel, Receiver, Sender};
use tokio::sync::oneshot;

use std::collections::HashSet;
use std::sync::Arc;
use tokio::runtime::Runtime;
use tokio::sync::Mutex;

use bt_hal::HalExports;
use bt_packet as packet;
use packet::{HciCommand, HciEvent};

use error::Result;

use facade::facade_module;

module! {
    hci_module,
    submodules {
        facade_module,
    },
    providers {
        HciExports => provide_hci,
    },
}

#[provides]
async fn provide_hci(hal_exports: HalExports, rt: Arc<Runtime>) -> HciExports {
    let (evt_tx, evt_rx) = channel::<HciEvent>(10);
    let (cmd_tx, cmd_rx) = mpsc::channel::<HciCommandEntry>(10);
    let hashset = Arc::new(Mutex::new(HashSet::new()));
    let pending_cmds = Arc::new(Mutex::new(Vec::new()));

    rt.spawn(on_event(
        pending_cmds.clone(),
        evt_tx.clone(),
        hal_exports.evt_rx,
    ));
    rt.spawn(on_command(pending_cmds, hal_exports.cmd_tx, cmd_rx));

    let evt_rx = Arc::new(Mutex::new(evt_rx));

    HciExports {
        cmd_tx,
        registered_events: Arc::clone(&hashset),
        evt_tx,
        evt_rx,
    }
}

/// HCI command entry
/// Uses a oneshot channel to wait until the event corresponding
/// to the command is received
#[derive(Debug)]
pub struct HciCommandEntry {
    /// The HCI command to send
    cmd: HciCommand,
    /// Transmit half of the oneshot
    fut: oneshot::Sender<HciCommand>,
}

#[derive(Debug)]
struct HciCommandEntryInner {
    opcode: u16,
    fut: oneshot::Sender<HciCommand>,
}

/// HCI interface
#[derive(Clone)]
pub struct HciExports {
    /// Transmit end of a channel used to send HCI commands
    cmd_tx: Sender<HciCommandEntry>,
    registered_events: Arc<Mutex<HashSet<u8>>>,
    evt_tx: Sender<HciEvent>,
    /// Receive channel half used to receive HCI events from the HAL
    pub evt_rx: Arc<Mutex<Receiver<HciEvent>>>,
}

impl HciExports {
    /// Send the HCI command
    async fn send(&mut self, cmd: HciCommand) -> Result<HciEvent> {
        let (tx, rx) = oneshot::channel::<HciEvent>();
        self.cmd_tx.send(HciCommandEntry { cmd, fut: tx }).await?;
        let event = rx.await?;
        Ok(event)
    }

    /// Send the HCI event
    async fn dispatch_event(&mut self, event: HciEvent) -> Result<()> {
        let evt_code = packet::get_evt_code(&event);
        if let Some(evt_code) = evt_code {
            let registered_events = self.registered_events.lock().await;
            if registered_events.contains(&evt_code) {
                self.evt_tx.send(event).await?;
            }
        }
        Ok(())
    }

    /// Enqueue an HCI command expecting a command complete
    /// response from the controller
    pub async fn enqueue_command_with_complete(&mut self, cmd: HciCommand) {
        let event = self.send(cmd).await.unwrap();
        self.dispatch_event(event).await.unwrap();
    }

    /// Enqueue an HCI command expecting a status response
    /// from the controller
    pub async fn enqueue_command_with_status(&mut self, cmd: HciCommand) {
        let event = self.send(cmd).await.unwrap();
        self.dispatch_event(event).await.unwrap();
    }

    /// Indicate interest in specific HCI events
    // TODO(qasimj): Add Sender<HciEvent> as an argument so that the calling
    // code can register its own event handler
    pub async fn register_event_handler(&mut self, evt_code: u8) {
        let mut registered_events = self.registered_events.lock().await;
        registered_events.insert(evt_code);
    }
}

async fn on_event(
    pending_cmds: Arc<Mutex<Vec<HciCommandEntryInner>>>,
    evt_tx: Sender<HciEvent>,
    evt_rx: Arc<Mutex<mpsc::UnboundedReceiver<HciEvent>>>,
) {
    while let Some(evt) = evt_rx.lock().await.recv().await {
        let opcode = packet::get_evt_opcode(&evt).unwrap();
        let mut pending_cmds = pending_cmds.lock().await;
        if let Some(pending_cmd) = remove_first(&mut pending_cmds, |entry| entry.opcode == opcode) {
            pending_cmd.fut.send(evt).unwrap();
        } else {
            evt_tx.send(evt).await.unwrap();
        }
    }
}

async fn on_command(
    pending_cmds: Arc<Mutex<Vec<HciCommandEntryInner>>>,
    cmd_tx: mpsc::UnboundedSender<HciCommand>,
    mut cmd_rx: mpsc::Receiver<HciCommandEntry>,
) {
    while let Some(cmd) = cmd_rx.recv().await {
        let mut pending_cmds = pending_cmds.lock().await;
        pending_cmds.push(HciCommandEntryInner {
            opcode: packet::get_cmd_opcode(&cmd.cmd).unwrap(),
            fut: cmd.fut,
        });
        cmd_tx.send(cmd.cmd).unwrap();
    }
}

fn remove_first<T, P>(vec: &mut Vec<T>, predicate: P) -> Option<T>
where
    P: FnMut(&T) -> bool,
{
    if let Some(i) = vec.iter().position(predicate) {
        Some(vec.remove(i))
    } else {
        None
    }
}
