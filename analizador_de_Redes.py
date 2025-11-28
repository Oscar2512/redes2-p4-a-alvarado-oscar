#!/usr/bin/env python3
"""
Servidor HTTP para procesamiento de datos Wi-Fi
Ejercicio X - Redes 2
"""

import http.server
import json
import re
import socketserver
import urllib.request
from typing import List, Dict, Any

class WiFiDataHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador de solicitudes HTTP para datos Wi-Fi"""
    
    def do_GET(self) -> None:
        """Maneja solicitudes GET"""
        if self.path == '/air':
            self._serve_wifi_data()
        else:
            self._serve_404()
    
    def _serve_wifi_data(self) -> None:
        """Sirve los datos Wi-Fi procesados en formato JSON"""
        try:
            wifi_data = self._fetch_and_parse_wifi_data()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(wifi_data, indent=2).encode('utf-8'))
            
        except Exception as e:
            self._serve_error(f"Error procesando datos: {str(e)}")
    
    def _serve_404(self) -> None:
        """Sirve error 404 para rutas no encontradas"""
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Ruta no encontrada. Use /air para obtener datos Wi-Fi.')
    
    def _serve_error(self, message: str) -> None:
        """Sirve mensaje de error"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        error_data = {"error": message}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def _fetch_and_parse_wifi_data(self) -> List[Dict[str, Any]]:
        """
        Descarga y parsea los datos Wi-Fi desde la URL remota
        
        Returns:
            List[Dict]: Lista de redes Wi-Fi procesadas
        """
        url = "https://mochila.laotra.red/public.php/dav/files/9TcBaPFWMQiEMsn/"
        
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        
        return self._parse_wifi_content(content)
    
    def _parse_wifi_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Parsea el contenido de texto en datos estructurados Wi-Fi
        
        Args:
            content (str): Contenido textual de los registros Wi-Fi
            
        Returns:
            List[Dict]: Lista de redes Wi-Fi parseadas
        """
        networks = []
        lines = content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            network = self._parse_wifi_line(line)
            if network:
                networks.append(network)
        
        return networks
    
    def _parse_wifi_line(self, line: str) -> Dict[str, Any]:
        """
        Parsea una línea individual de datos Wi-Fi
        
        Args:
            line (str): Línea de texto con datos Wi-Fi
            
        Returns:
            Dict: Datos de red Wi-Fi parseados
        """
        # Expresión regular para capturar campos, manejando comillas
        pattern = r'([^,"]+|"[^"]*")'
        fields = re.findall(pattern, line)
        
        # Limpiar campos de comillas y espacios
        cleaned_fields = [field.strip('"').strip() for field in fields if field.strip()]
        
        # Mapear campos a la estructura esperada
        return {
            "bss": cleaned_fields[0] if len(cleaned_fields) > 0 else "",
            "tsf": cleaned_fields[1] if len(cleaned_fields) > 1 else "",
            "freq": float(cleaned_fields[2]) if len(cleaned_fields) > 2 and cleaned_fields[2] else 0.0,
            "beacon": int(cleaned_fields[3]) if len(cleaned_fields) > 3 and cleaned_fields[3] else 0,
            "capa": cleaned_fields[4] if len(cleaned_fields) > 4 else "0x0",
            "signal": float(cleaned_fields[5]) if len(cleaned_fields) > 5 and cleaned_fields[5] else 0.0,
            "ssid": cleaned_fields[6] if len(cleaned_fields) > 6 else "",
            "ht_capa": cleaned_fields[7] if len(cleaned_fields) > 7 else "0x0",
            "primary_channel": int(cleaned_fields[8]) if len(cleaned_fields) > 8 and cleaned_fields[8] else 0,
            "vht_capa": cleaned_fields[9] if len(cleaned_fields) > 9 else "0x0",
            "he_capa": cleaned_fields[10] if len(cleaned_fields) > 10 else "0x0",
            "he_phy_capa": cleaned_fields[11] if len(cleaned_fields) > 11 else "",
            "encryption": cleaned_fields[12] if len(cleaned_fields) > 12 else "",
            "cipher": cleaned_fields[13] if len(cleaned_fields) > 13 else "",
            "suite": cleaned_fields[14] if len(cleaned_fields) > 14 else ""
        }

def run_server(port: int = 8000) -> None:
    """Inicia el servidor HTTP en el puerto especificado"""
    handler = WiFiDataHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Servidor Wi-Fi ejecutándose en http://localhost:{port}")
        print("Acceda a /air para obtener los datos en formato JSON")
        print("Presione Ctrl+C para detener el servidor")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDeteniendo servidor...")

if __name__ == "__main__":
    run_server()