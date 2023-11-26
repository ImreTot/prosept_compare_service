import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "./ui/button"

const List = () => {
  return (
    <div className="p-2">
      <h2 className="text-center text-xl font-bold my-4">Просепт</h2>
      <div className="h-40 grid gap-4">
        <Card className="">
          <CardHeader>
            <CardTitle>Prosept rust remover</CardTitle>
            <CardDescription>0.5 арктикул 023-05 обьем 0.5л</CardDescription>
          </CardHeader>
          <CardContent>
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button>Cопоставить</Button>
          </CardFooter>
        </Card>
        <Card className="">
          <CardHeader>
            <CardTitle>Prosept rust remover</CardTitle>
            <CardDescription>0.5 арктикул 023-05 обьем 0.5л</CardDescription>
          </CardHeader>
          <CardContent>
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button>Cопоставить</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

export default List