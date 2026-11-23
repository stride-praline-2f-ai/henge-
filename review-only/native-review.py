from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import tempfile
import threading
import sys

source=Path(sys.argv[1]).resolve()
machines=(source/'ios/Henge/Machines.swift').read_text()
def section(a,b):
    start=machines.index(a)
    return machines[start:machines.index(b,start)]
machine_methods=section('    private func adopt(', '    /// Makes a folder') + section('    private func writeExport(', '    /// A machine made here')
fixture=r'''
import Foundation
import Darwin
private let fm=FileManager.default
private let tempRoot=URL(fileURLWithPath:CommandLine.arguments[1],isDirectory:true)
private struct MachineFile:Codable {var name:String?;var ecid:UInt64;var seed:UInt64?;var ramMB:Int?}
private struct VirtualMac {
    var id=UUID()
    var name:String
    var ecid:UInt64
    var seed:UInt64
    var ramMB:Int
    var diskBytes:Int64
    var directory:URL {tempRoot.appendingPathComponent("machines",isDirectory:true).appendingPathComponent(id.uuidString,isDirectory:true)}
    var rom:URL {directory.appendingPathComponent("AVPBooter.vmapple2.bin")}
    var disk:URL {directory.appendingPathComponent("disk.img")}
    var aux:URL {directory.appendingPathComponent("auxiliary.bin")}
}
private enum Device {static let name="review fixture"}
private enum ByteText {static func string(_ bytes:UInt64)->String {String(bytes)}}
private enum HengeLog {static func log(_ category:String,_ message:String) {}}
typealias Progress=(UInt64,UInt64,OpaquePointer?)->Void
func hv_sparse_pack_progress(_ s:String,_ t:String,_ p:Progress,_ c:OpaquePointer?)->Int32 {-1}
func hv_sparse_unpack(_ s:String,_ t:String,_ p:Progress,_ c:OpaquePointer?)->Int32 {-1}
@MainActor private final class Machines {
    static let root=tempRoot
    static let inbox=tempRoot.appendingPathComponent("inbox",isDirectory:true)
    static let required=["AVPBooter.vmapple2.bin","auxiliary.bin","machine.json"]
    static let packedDisk="disk.img.hvsparse"
    static let shared=Machines()
    var importing:String?,lastError:String?
    var unpacked=0.0,exported=0.0
    var all:[VirtualMac]=[]
    static func hasDisk(_ url:URL)->Bool {
        ["disk.img",packedDisk].contains {fm.fileExists(atPath:url.appendingPathComponent($0).path)}
    }
    func excludeFromBackup(){}
    func save(){}
    func message(_ text:String)->NSError {NSError(domain:"audit",code:1,userInfo:[NSLocalizedDescriptionKey:text])}
''' + machine_methods + r'''
    func verifyFailures() async throws {
        let inbox=Self.inbox.appendingPathComponent("Mac",isDirectory:true)
        try fm.createDirectory(at:inbox,withIntermediateDirectories:true)
        let rom=inbox.appendingPathComponent("AVPBooter.vmapple2.bin")
        let aux=inbox.appendingPathComponent("auxiliary.bin")
        let meta=inbox.appendingPathComponent("machine.json")
        let packed=inbox.appendingPathComponent(Self.packedDisk)
        let bytes=Data([1,2,3])
        for file in [rom,aux,packed] {try bytes.write(to:file)}
        try Data(#"{"name":"Audit","ecid":12345}"#.utf8).write(to:meta)
        await adopt(inbox,move:true)
        precondition(all.isEmpty && lastError != nil)
        precondition(fm.fileExists(atPath:packed.path))
        precondition([rom,aux,meta].allSatisfy {!fm.fileExists(atPath:$0.path)})
        print("REPRODUCED automatic import loses the moved boot and identity files if unpacking fails")

        let mac=VirtualMac(name:"Existing backup",ecid:12,seed:0,ramMB:2048,diskBytes:0)
        try fm.createDirectory(at:mac.directory,withIntermediateDirectories:true)
        let previous=Self.inbox.appendingPathComponent("Exports",isDirectory:true)
            .appendingPathComponent(mac.name,isDirectory:true)
        try fm.createDirectory(at:previous,withIntermediateDirectories:true)
        let contents=previous.appendingPathComponent(Self.packedDisk)
        try bytes.write(to:contents)
        for file in [mac.rom,mac.aux,mac.disk] {try bytes.write(to:file)}
        do {
            _=try await writeExport(mac)
            fatalError("injected export failure should return an error")
        } catch {
            precondition(!fm.fileExists(atPath:contents.path))
            print("REPRODUCED a failed replacement export deletes the previous valid backup")
        }
    }
}
@main struct Run {
    @MainActor static func main() async throws {
        try await Machines.shared.verifyFailures()
        let url=URL(string:CommandLine.arguments[2])!
        let part=tempRoot.appendingPathComponent("installer.part")
        try Data([1,2,3]).write(to:part)
        let download=RangedDownload(url:url,part:part){_,_ in}
        try await download.run()
        guard RangedDownload.size(of:part)==3 else {fatalError("unexpected fixture size")}
        print("REPRODUCED ranged download declares success with a partial file after unverifiable 416")
    }
}
'''
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if self.headers.get('Range')!='bytes=3-':
            self.send_error(400)
            return
        self.send_response(416)
        self.send_header('Content-Length','0')
        self.end_headers()

with tempfile.TemporaryDirectory(prefix='henge-audit-native-') as temp, ThreadingHTTPServer(('127.0.0.1',0),Handler) as server:
    out=Path(temp)
    (out/'fixture.swift').write_text(fixture)
    command=['xcrun','--sdk','macosx','swiftc','-swift-version','5','-parse-as-library',
             str(source/'ios/Henge/RangedDownload.swift'),str(out/'fixture.swift'),'-o',str(out/'verify')]
    subprocess.run(command,check=True)
    t=threading.Thread(target=server.serve_forever,daemon=True)
    t.start()
    try:
        subprocess.run([str(out/'verify'),str(out),f'http://127.0.0.1:{server.server_port}/installer'],check=True,timeout=25)
    finally:
        server.shutdown()
        t.join()
