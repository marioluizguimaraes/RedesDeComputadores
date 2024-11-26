import java.util.Objects;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {

        Scanner entrada = new Scanner(System.in);

        System.out.println("-------------------------------------------------------------");

        System.out.println("ATENÇÃO: O IP e a Mascara deve ser digitado no formato 255.255.255.255 !");

        System.out.println("-------------------------------------------------------------");

        System.out.print("Digite o primeiro endereço IP: ");
        String enderecoip1 = entrada.next();

        System.out.print("Digite o segundo endereço IP: ");
        String enderecoip2 = entrada.next();

        System.out.print("Digite a mascara de rede: ");
        String mascara = entrada.next();

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
}