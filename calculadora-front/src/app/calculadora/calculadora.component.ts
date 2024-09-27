import { Component, ElementRef, ViewChild } from '@angular/core';
import { FileUploadService } from '../services/file-upload.service';

@Component({
  selector: 'app-calculadora',
  templateUrl: './calculadora.component.html',
  styleUrls: ['./calculadora.component.css']
})
export class CalculadoraComponent {

  isdecimaB = false;

  input: string = '';
  history: string[] = [];
  buttons: string[] = ['7', '8', '9', '/', '4', '5', '6', '*', '1', '2', '3', '-', '0', '.', '=', '+', 'C'];

  @ViewChild('historyContainer') historyContainer!: ElementRef;

  constructor(private fileUploadService: FileUploadService) { }


  pressButton(value: string) {
    if (value === 'C') {
      this.input = '';
    } else if (value === '=') {
      try {

        if (this.isdecimaB) {

          // Convertir la entrada a número
          const numberInput = Number(this.input);

          if (!isNaN(numberInput)) { // Verificar si numberInput es un número válido
            this.input = numberInput.toString(2); // Conversión a binario
            console.log(`El número decimal ${numberInput} en binario es: ${this.input}`);
            console.log('this.input', this.input);
            this.history.push(`D/B  ${numberInput} = ${this.input}`)
            this.scrollToBottom();
          }



        } else {
          const result = eval(this.input); // Usar eval con precaución
          this.history.push(`${this.input} = ${result}`);
          this.input = result.toString();
          this.scrollToBottom();
        }

      } catch (error) {
        this.input = 'Error'
      }
    } else {
      this.input += value
    }
  }


  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {

      if (this.isdecimaB) {
        this.fileUploadService.convertToBynary(file).subscribe(
          (result: any) => {
            console.log('result', result);
            this.input = result.binario
            this.history.push(`D/B  ${result.text} = ${this.input}`)
            this.scrollToBottom();
          }
        )
      } else {
        this.fileUploadService.uploadFile(file).subscribe(
          (result: any) => {
            console.log('result', result);
            this.input = result.calculo;
            this.history.push(`${result.text} = ${this.input}`)
            this.scrollToBottom();
          });
      }



    }
  }

  scrollToBottom() {
    const container = this.historyContainer.nativeElement;
    container.scrollTop = container.scrollHeight;
  }


  cambiarDecialBinario() {
    this.isdecimaB = !this.isdecimaB
    console.log('this.isdecimaB', this.isdecimaB);
  }


  get buttonColor() {
    return this.isdecimaB ? 'bg-green-700' : 'bg-gray-700';

  }
}
