import java.util.Objects;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {

        Scanner entrada = new Scanner(System.in);

        System.out.print("Digite o primeiro endereço IP: ");
        String enderecoip1 = entrada.next();

        if (!validarEnderecoIP(enderecoip1)) {
            System.out.println("Endereço IP inválido!");
            return;
        }

        System.out.print("Digite o segundo endereço IP: ");
        String enderecoip2 = entrada.next();

        if (!validarEnderecoIP(enderecoip2)) {
            System.out.println("Endereço IP inválido!");
            return;
        }

        System.out.print("Digite a mascara de rede: ");
        String mascara = entrada.next();

        if (!validarMascaraDeRede(mascara)) {
            System.out.println("Máscara de rede inválida!");
            return;
        }

        System.out.println("-------------------------------------------------------------");

        EnderecoIP ip1 = new EnderecoIP(enderecoip1, mascara);
        System.out.println("Primeiro Endereço Ip: " + ip1.getIp());
        System.out.println("Mascara: " + ip1.getMascara());
        System.out.println("Endereço Broadcast: " + ip1.broadcastDaRede(ip1.getMascara()));

        System.out.println("-------------------------------------------------------------");

        EnderecoIP ip2 = new EnderecoIP(enderecoip2, mascara);
        System.out.println("Segundo Endereço Ip: " + ip2.getIp());
        System.out.println("Mascara: " + ip2.getMascara());
        System.out.println("Endereço Broadcast: " + ip2.broadcastDaRede(ip2.getMascara()));

        System.out.println("-------------------------------------------------------------");

        System.out.println(Objects.equals(ip1.broadcastDaRede(ip1.getMascara()), ip2.broadcastDaRede(ip2.getMascara())) ? "SIM" : "NÃO");
    }

    public static boolean validarEnderecoIP(String endereco) {
        String[] octetos = endereco.split("\\.");

        if (octetos.length != 4) return false;

        try {
            for (String octeto : octetos) {
                if (Integer.parseInt(octeto) < 0 || Integer.parseInt(octeto) > 255) return false;
            }
        } catch (NumberFormatException e) {
            return false;
        }

        return true;
    }

    public static boolean validarMascaraDeRede(String mascara) {
        String[] octetos = mascara.split("\\.");

        if (octetos.length != 4) return false;

        try {
            int[] valores = new int[4];
            for (int i = 0; i < 4; i++) {
                valores[i] = Integer.parseInt(octetos[i]);
                if (valores[i] < 0 || valores[i] > 255) return false;
            }

            for (int i = 0; i < valores.length; i++) {
                if (valores[i] < 255 && valores[i-1] < 255) return false;
            }
        } catch (NumberFormatException e) { return false; }
        return true;
    }
}